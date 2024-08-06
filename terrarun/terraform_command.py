# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

import datetime
import json
import os
import subprocess
import threading
from enum import Enum
from time import sleep
from typing import Dict

import sqlalchemy.orm

import terrarun.models.audit_event
import terrarun.models.run
from terrarun.database import Database
from terrarun.logger import get_logger
from terrarun.models.base_object import BaseObject
from terrarun.models.blob import Blob
import terrarun.utils


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

    def get_status_change_timestamps(self) -> Dict[TerraformCommandState, datetime.datetime]:
        """Get timestamps for status changes"""
        session = Database.get_session()
        return {
            TerraformCommandState(Database.decode_blob(event.new_value)): event.timestamp
            for event in session.query(terrarun.models.audit_event.AuditEvent).where(
                terrarun.models.audit_event.AuditEvent.object_id==self.id,
                terrarun.models.audit_event.AuditEvent.object_type==self.ID_PREFIX,
                terrarun.models.audit_event.AuditEvent.event_type==terrarun.models.audit_event.AuditEventType.STATUS_CHANGE
            )
        }
