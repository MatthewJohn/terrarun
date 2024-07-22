# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

import json
import os
import subprocess
import threading
from enum import Enum
from time import sleep

import sqlalchemy.orm

import terrarun.models.audit_event
import terrarun.models.run
from terrarun.database import Database
from terrarun.logger import get_logger
from terrarun.models.base_object import BaseObject
from terrarun.models.blob import Blob

logger = get_logger(__name__)


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

    def append_output(self, data, no_append=False):
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
        if no_append:
            log.data = data
        else:
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
            if obj.run.status == terrarun.models.run.RunStatus.CANCELED:
                command_proc.kill()
                break
            sleep(0.5)
        session.close()

    def _run_command(self, command, work_dir, environment_variables=None):
        """Run system command, pping output into output object"""

        if environment_variables is None:
            environment_variables = os.environ.copy()

        try:
            logger.info('Running command: %s', command)
            command_proc = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=work_dir,
                env=environment_variables)
        except:
            self.append_output(b'An error occured whilst starting the run')
            return 255

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
                    self.append_output(b'To perform exactly these actions, run the following command to apply:\n    terraform apply\n')
                    print_lines = False

                if print_lines:
                    self.append_output(line)
            elif command_proc.poll() is not None:
                break

        return command_proc.returncode

    def add_output(self, output):
        """Record command output."""
        with Database.get_session() as session:
            self.output += output
            session.commit()

    def update_status(self, new_status, session=None):
        """Update state of plan."""
        logger.info("Updating %s status to from %s to %s", self.ID_PREFIX, self.status, new_status)
        should_commit = False
        if session is None:
            session = Database.get_session()
            session.refresh(self)
            should_commit = True

        audit_event = terrarun.models.audit_event.AuditEvent(
            organisation=self.run.configuration_version.workspace.organisation,
            object_id=self.id,
            object_type=self.ID_PREFIX,
            old_value=Database.encode_value(self.status.value) if self.status else None,
            new_value=Database.encode_value(new_status.value),
            event_type=terrarun.models.audit_event.AuditEventType.STATUS_CHANGE)

        self.status = new_status
        session.add(self)
        session.add(audit_event)
        if should_commit:
            session.commit()

    @property
    def status_timestamps(self):
        """Return dict of status timestamps for API"""

        session = Database.get_session()
        def convert_event_name(event):
            name = Database.decode_blob(event)
            if name == TerraformCommandState.RUNNING:
                name = 'started'
            return '{}-at'.format(name.replace('_', '-'))
        return {
            convert_event_name(event.new_value): terrarun.utils.datetime_to_json(event.timestamp)
            for event in session.query(terrarun.models.audit_event.AuditEvent).where(
                terrarun.models.audit_event.AuditEvent.object_id==self.id,
                terrarun.models.audit_event.AuditEvent.object_type==self.ID_PREFIX,
                terrarun.models.audit_event.AuditEvent.event_type==terrarun.models.audit_event.AuditEventType.STATUS_CHANGE)
        }
