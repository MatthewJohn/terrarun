
from enum import Enum
import json
import os
import subprocess
import threading
from time import sleep

import sqlalchemy.orm

from terrarun.base_object import BaseObject
from terrarun.blob import Blob
from terrarun.database import Database
import terrarun.run
from terrarun.state_version import StateVersion


class TerraformCommandState(Enum):

    PENDING = 'pending'
    MANAGE_QUEUED = 'managed_queued'
    QUEUED = 'queued'
    RUNNING = 'running'
    ERRORED = 'errored'
    CANCELED = 'canceled'
    FINISHED = 'finished'
    UNREACHABLE = 'unreachable'


class TerraformCommand(BaseObject):

    STATE_FILE = 'terraform.tfstate'
    PLAN_OUTPUT_FILE = 'TFRUN_PLAN_OUT'

    def _pull_latest_state(self, work_dir):
        """Pull latest version of state to working copy."""
        # No latest state available for workspace
        state_version = self.run.configuration_version.workspace.latest_state
        if not state_version or not state_version.state_json:
            return

        with open(os.path.join(work_dir, self.STATE_FILE), 'w') as state_fh:
            state_fh.write(json.dumps(state_version.state_json))

    def _append_output(self, data):
        """Append to output"""
        session = Database.get_session()
        session.refresh(self)
        if self.log_id is None:
            log = Blob(data=b"")
            self.log = log
            session.add(self)
        else:
            log = self.log
            session.refresh(log)
        log.data += data
        session.add(log)
        session.commit()

    def execute(self):
        raise NotImplementedError

    @classmethod
    def _command_cancel_check(cls, obj_id, command_proc):
        """Check for command cancel"""
        session = sqlalchemy.orm.Session(Database.get_engine())
        obj = session.query(cls).filter(cls.id==obj_id).first()
        while command_proc.poll() is None:
            session.refresh(obj)
            if obj.run.status == terrarun.run.RunStatus.CANCELED:
                command_proc.kill()
                break
            sleep(0.5)
        session.close()

    def _run_command(self, command, work_dir):
        command_proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=work_dir)
        cancel_monitor = threading.Thread(
            target=self.__class__._command_cancel_check,
            args=(self.id, command_proc,))
        cancel_monitor.start()

        # Obtain all stdout
        print_lines = True
        while True:
            line = command_proc.stdout.readline()
            if line:
                # Stop printing lines once line about
                # saving plan to output file is displayed and
                # display line about how to apply changes
                if line.startswith(b'Saved the plan to: '):
                    self._append_output(b'To perform exactly these actions, run the following command to apply:\n    terraform apply\n')
                    print_lines = False

                if print_lines:
                    self._append_output(line)
            elif command_proc.poll() is not None:
                break

        return command_proc.returncode

    def add_output(self, output):
        """Record command output."""
        with Database.get_session() as session:
            self.output += output
            session.commit()
