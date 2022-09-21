# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from enum import Enum
import re
import sqlalchemy
import sqlalchemy.orm

from terrarun.base_object import BaseObject
from terrarun.database import Base, Database
from terrarun.task_result import TaskResult, TaskResultStatus
from terrarun.workspace_task import WorkspaceTaskStage


class TaskStageStatus(Enum):
    """Task stage statuses"""

    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERRRORED = "errored"
    CANCELED = "canceled"
    UNREACHABLE = "unreachable"


class TaskStage(Base, BaseObject):

    ID_PREFIX = 'ts'

    __tablename__ = 'task_stage'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    stage = sqlalchemy.Column(sqlalchemy.Enum(WorkspaceTaskStage))
    status = sqlalchemy.Column(sqlalchemy.Enum(TaskStageStatus))

    run_id = sqlalchemy.Column(sqlalchemy.ForeignKey("run.id"), nullable=False)
    run = sqlalchemy.orm.relationship("Run", back_populates="task_stages")

    task_results = sqlalchemy.orm.relationship("TaskResult", back_populates="task_stage")

    @classmethod
    def create(cls, run, stage, workspace_tasks):
        """Create task stage and task result objects"""
        # Create task stage
        session = Database.get_session()
        task_stage = cls(run=run, stage=stage, status=TaskStageStatus.PENDING)
        session.add(task_stage)

        # Create result objects for each workspace task
        for workspace_task in workspace_tasks:
            task_result = TaskResult(workspace_task=workspace_task, task_stage=task_stage, status=TaskResultStatus.PENDING)
            session.add(task_result)
        session.commit()

        return task_stage

    def update_attributes(self, **kwargs):
        """Update attributes of task"""

        if 'id' in kwargs or 'organisation' in kwargs:
            # Do not allow update of ID or organisation
            return False

        # If name is specificed in arguments to update,
        # check it is valid
        if ('name' in kwargs and
                kwargs['name'] != self.name and
                not self.validate_new_name(self.organisation, kwargs['name'])):
            return False

        for attr in kwargs:
            setattr(self, attr, kwargs[attr])

        session = Database.get_session()
        session.add(self)
        session.commit()

    def get_relationship(self):
        """Return relationship data for tag."""
        return {
            "id": self.api_id,
            "type": "task-stages"
        }

    def get_api_details(self):
        """Return API details for task"""
        return {
            "id": self.api_id,
            "type": "task-stages",
            "attributes": {
                "status": self.status.value,
                "stage": self.stage.value,
                "status-timestamps": {
                    "passed-at": "2022-06-08T20:32:12+08:00",
                    "running-at": "2022-06-08T20:32:11+08:00"
                },
                "created-at": "2022-06-08T12:31:56.94Z",
                "updated-at": "2022-06-08T12:32:12.315Z"
            },
            "relationships": {
                "run": {
                    "data": {
                        "id": self.run.api_id,
                        "type": "runs"
                    }
                },
                "task-results": {
                    "data": [
                        {
                            "id": task_result.api_id,
                            "type": "task-results"
                        } for task_result in self.task_results
                    ]
                }
            },
            "links": {
                "self": f"/api/v2/task-stages/{self.api_id}"
            }
        }
