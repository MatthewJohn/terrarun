# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

from enum import Enum

import sqlalchemy
import sqlalchemy.orm

from terrarun.models.base_object import BaseObject
from terrarun.database import Base, Database


class WorkspaceTaskEnforcementLevel(Enum):
    """Enforcement type of workspace task"""
    ADVISORY = "advisory"
    MANDATORY = "mandatory"


class WorkspaceTaskStage(Enum):
    """Stage of workspace task"""
    PRE_PLAN = "pre_plan"
    POST_PLAN = "post_plan"
    PRE_APPLY = "pre_apply"


class WorkspaceTask(Base, BaseObject):
    """Define workspace tasks."""

    ID_PREFIX = "wstask"

    __tablename__ = "workspace_task"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    api_id_fk = sqlalchemy.Column(sqlalchemy.ForeignKey("api_id.id"), nullable=True)
    api_id_obj = sqlalchemy.orm.relationship("ApiId", foreign_keys=[api_id_fk])

    workspace_id = sqlalchemy.Column(sqlalchemy.ForeignKey("workspace.id"))
    workspace = sqlalchemy.orm.relationship("Workspace", back_populates="workspace_tasks")
    task_id = sqlalchemy.Column(sqlalchemy.ForeignKey("task.id"))
    task = sqlalchemy.orm.relationship("Task", back_populates="workspace_tasks")

    active = sqlalchemy.Column(sqlalchemy.Boolean, default=True)

    enforcement_level = sqlalchemy.Column(sqlalchemy.Enum(WorkspaceTaskEnforcementLevel))
    stage = sqlalchemy.Column(sqlalchemy.Enum(WorkspaceTaskStage))

    task_results = sqlalchemy.orm.relationship("TaskResult", back_populates="workspace_task")

    def delete(self):
        """Delete workspace task association"""
        session = Database.get_session()
        self.active = False
        session.add(self)
        session.commit()

    def get_api_details(self):
        """Return API details"""
        return {
            "data": {
                "id": self.api_id,
                "type": "workspace-tasks",
                "attributes": {
                    "enforcement-level": self.enforcement_level.value,
                    "stage": self.stage.value
                },
                "relationships": {
                    "task": {
                        "data": {
                            "id": self.task.api_id,
                            "type": "tasks"
                        }
                    },
                    "workspace": {
                        "data": {
                            "id": self.workspace.api_id,
                            "type": "workspaces"
                        }
                    }
                },
                "links": {
                    "self": f"/api/v2/workspaces/{self.workspace.api_id}/tasks/{self.task.api_id}"
                }
            }
        }
