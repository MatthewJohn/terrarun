# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

import datetime
from enum import Enum
from typing import List

import sqlalchemy
import sqlalchemy.orm

import terrarun.models.run
import terrarun.models.run_flow
import terrarun.terraform_command
import terrarun.utils
import terrarun.models.task_result
from terrarun.database import Base, Database
from terrarun.logger import get_logger
from terrarun.models.base_object import BaseObject, update_object_status
from terrarun.models.task_result import TaskResult, TaskResultStatus
from terrarun.models.workspace_task import (
    WorkspaceTaskEnforcementLevel,
    WorkspaceTaskStage,
)


logger = get_logger(__name__)

class TaskStageStatus(Enum):
    """Task stage statuses"""

    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERRORED = "errored"
    CANCELED = "canceled"
    UNREACHABLE = "unreachable"


class TaskStage(Base, BaseObject):

    ID_PREFIX = 'ts'

    __tablename__ = 'task_stage'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    api_id_fk = sqlalchemy.Column(sqlalchemy.ForeignKey("api_id.id"), nullable=True)
    api_id_obj = sqlalchemy.orm.relationship("ApiId", foreign_keys=[api_id_fk])

    stage = sqlalchemy.Column(sqlalchemy.Enum(WorkspaceTaskStage))
    status = sqlalchemy.Column(sqlalchemy.Enum(TaskStageStatus))

    run_id = sqlalchemy.Column(sqlalchemy.ForeignKey("run.id"), nullable=False)
    run = sqlalchemy.orm.relationship("Run", back_populates="task_stages")

    task_results: List['terrarun.models.task_result.TaskResult'] = sqlalchemy.orm.relationship("TaskResult", back_populates="task_stage")

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

    @property
    def organisation(self):
        """Return organisation."""
        return self.run.configuration_version.workspace.organisation

    def check_status(self):
        """Check status of tasks and update statuses accordingly"""
        # Iterate through each task stage result
        still_running = 0
        for task_result in self.task_results:
            is_mandatory = task_result.workspace_task.enforcement_level is WorkspaceTaskEnforcementLevel.MANDATORY

            # If task result was cancelled and the
            # check is mandatory, move to complete
            if task_result.status is TaskResultStatus.CANCELED and is_mandatory:
                update_object_status(self, TaskStageStatus.CANCELED)
                self.run.update_status(terrarun.models.run_flow.RunStatus.CANCELED)
                if self.stage is WorkspaceTaskStage.PRE_PLAN:
                    # Since plan already exists, mark as failed
                    self.run.plan.append_output(b'Plan was not executed due to cancellation of mandatory pre-plan task(s)')
                    self.run.plan.update_status(terrarun.terraform_command.TerraformCommandState.ERRORED)
                return False, False

            # Check if any mandatory tasks have errored
            elif (task_result.status in [
                    TaskResultStatus.FAILED,
                    TaskResultStatus.ERRORED,
                    TaskResultStatus.UNREACHABLE] and
                    is_mandatory):

                # Update task stage, plan and run statuses
                task_stage_status = (
                    TaskStageStatus.FAILED
                    if task_result.status is TaskResultStatus.FAILED else (
                        TaskStageStatus.ERRORED if task_result.status is TaskResultStatus.ERRORED else TaskStageStatus.UNREACHABLE
                    )
                )
                self.set_errored(task_stage_status)
                return False, False

            # If task is still running, check if time has elapsed
            elif task_result.status in [TaskResultStatus.PENDING, TaskResultStatus.RUNNING]:
                if (task_result.start_time and
                        (task_result.start_time + datetime.timedelta(minutes=10)) <
                        datetime.datetime.now()):
                    # Update task result status to errored
                    update_object_status(task_result, TaskResultStatus.ERRORED)
                    # If task is mandatory, treat run as errored
                    if is_mandatory:
                        self.set_errored()
                        return False, False
                still_running += 1
            
            else:
                logger.error('task result combination that is not covered. Status: %s. Mandatory: %s', task_result.status, is_mandatory)

        # If no tasks are still running, update
        # state to completed
        if not still_running:
            update_object_status(self, TaskStageStatus.PASSED)
            # Return to indicate that the run has not errored
            # and that the task stage is complete
            return True, True

        # Return True to indicate that that the run is still
        # in progress, and False to indicate the task stage is not complete
        return True, False

    def set_errored(self, task_stage_status=None):
        """Set task stage and associated resources as errored."""
        if task_stage_status is None:
            task_stage_status = TaskStageStatus.ERRORED
        # Update task stage, plan and run statuses
        update_object_status(self, task_stage_status)
        if self.stage is WorkspaceTaskStage.PRE_PLAN:
            self.run.plan.append_output(b'Plan was not executed due to failure of mandatory pre-plan task(s)')
            self.run.plan.update_status(terrarun.terraform_command.TerraformCommandState.CANCELED)
        self.run.update_status(terrarun.models.run_flow.RunStatus.ERRORED)

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
