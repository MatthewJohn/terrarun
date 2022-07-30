
from enum import Enum
import json
import os
import subprocess

from terrarun.base_object import BaseObject
from terrarun.blob import Blob
from terrarun.database import Database
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

    def _run_command(self, command, work_dir):
        command_proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=work_dir)

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

    def generate_state_version(self):
        """Generate state version from state file."""
        state_content = None
        with open(os.path.join(self._run._configuration_version._extract_dir, 'terraform.tfstate'), 'r') as state_file_fh:
            state_content = state_file_fh.readlines()
        state_json = json.loads('\n'.join(state_content))
        self._state_version = StateVersion.create_from_state_json(run=self._run, state_json=state_json)

        # Register state with workspace
        self.run.configuration_version.workspace.latest_state = self._state_version