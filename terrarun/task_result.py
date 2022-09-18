# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from enum import Enum
import re
import sqlalchemy
import sqlalchemy.orm

from terrarun.base_object import BaseObject
from terrarun.utils import update_object_status
from terrarun.blob import Blob
from terrarun.database import Base, Database
from terrarun.workspace_task import WorkspaceTaskStage


class TaskResultStatus(Enum):
    """Task stage statuses"""

    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERRRORED = "errored"
    CANCELED = "canceled"
    UNREACHABLE = "unreachable"


class TaskResult(Base, BaseObject):

    ID_PREFIX = 'taskrs'

    __tablename__ = 'task_result'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    status = sqlalchemy.Column(sqlalchemy.Enum(TaskResultStatus))
    message_id = sqlalchemy.Column(sqlalchemy.ForeignKey("blob.id"), nullable=True)
    _message = sqlalchemy.orm.relation("Blob", foreign_keys=[message_id])

    task_stage_id = sqlalchemy.Column(sqlalchemy.ForeignKey("task_stage.id"), nullable=False)
    task_stage = sqlalchemy.orm.relationship("TaskStage", back_populates="task_results")

    workspace_task_id = sqlalchemy.Column(sqlalchemy.ForeignKey("workspace_task.id"), nullable=False)
    workspace_task = sqlalchemy.orm.relationship("WorkspaceTask", back_populates="task_results")

    @property
    def message(self):
        """Return plan output value"""
        if self._plan_output_binary and self._plan_output_binary.data:
            return self._plan_output_binary.data
        return {}

    @message.setter
    def message(self, value):
        """Set message"""
        session = Database.get_session()

        if self._plan_output_binary:
            message = self._message
            session.refresh(message)
        else:
            message = Blob()

        message.data = value

        session.add(message)
        session.refresh(self)
        self._message = message
        session.add(self)
        session.commit()

    @property
    def organisation(self):
        """Return organisation"""
        return self.workspace_task.workspace.organisation

    def execute(self):
        """Execute task"""
        update_object_status(self, TaskResultStatus.RUNNING)
        update_object_status(self, TaskResultStatus.PASSED)

    def get_api_details(self):
        """Return API details for task"""
        return {
            "id": self.api_id,
            "type": "task-results",
            "attributes": {
                "message": "No issues found.\nSeverity threshold is set to low.",
                "status": self.status.value,
                "status-timestamps": {
                    "passed-at": "2022-06-08T20:32:12+08:00",
                    "running-at": "2022-06-08T20:32:11+08:00"
                },
                "url": "https://external.service/project/task-123abc",
                "created-at": "2022-06-08T12:31:56.954Z",
                "updated-at": "2022-06-08T12:32:12.27Z",
                "task-id": self.workspace_task.task.api_id,
                "task-name": self.workspace_task.task.name,
                "task-url": self.workspace_task.task.url,
                "stage": self.task_stage.stage.value,
                "is-speculative": False,
                "workspace-task-id": self.workspace_task.api_id,
                "workspace-task-enforcement-level": self.workspace_task.enforcement_level.value
            },
            "relationships": {
                "task-stage": {
                    "data": {
                        "id": self.task_stage.api_id,
                        "type": "task-stages"
                    }
                }
            },
            "links": {
                "self": f"/api/v2/task-results/{self.api_id}"
            }
        }