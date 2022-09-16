# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from enum import Enum

import sqlalchemy
import sqlalchemy.orm

from terrarun.base_object import BaseObject
from terrarun.database import Base


class WorkspaceTaskEnforcementLevel(Enum):
    """Enforcement type of workspace task"""
    ADVISORY = "advisory"
    MANDATORY = "mandatory"


class WorkspaceTaskStage(Enum):
    """Stage of workspace task"""
    PRE_PLAN = "pre_plan"
    POST_PLAN = "post_plan"
    POST_APPLY = "pre_apply"


class WorkspaceTask(Base, BaseObject):
    """Define workspace tasks."""

    ID_PREFIX = "wstask"

    __tablename__ = "workspace_task"

    workspace_id = sqlalchemy.Column(sqlalchemy.ForeignKey("workspace.id"), primary_key=True)
    workspace = sqlalchemy.orm.relationship("Workspace", back_populates="workspace_tasks")
    task_id = sqlalchemy.Column(sqlalchemy.ForeignKey("task.id"), primary_key=True)
    task = sqlalchemy.orm.relationship("Task", back_populates="workspace_tasks")

    enforcement_level = sqlalchemy.Column(sqlalchemy.Enum(WorkspaceTaskEnforcementLevel))
    stage = sqlalchemy.Column(sqlalchemy.Enum(WorkspaceTaskStage))
