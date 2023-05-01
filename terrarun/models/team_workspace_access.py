# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from enum import Enum
import sqlalchemy
import sqlalchemy.orm

from terrarun.models.base_object import BaseObject
from terrarun.database import Base


class TeamWorkspaceAccessType(Enum):
    """Team workspace access types."""

    READ = "read"
    PLAN = "plan"
    WRITE = "write"
    ADMIN = "admin"
    CUSTOM = "custom"


class TeamWorkspaceRunsPermission(Enum):
    """Team workspace permissions for runs"""
    READ = "read"
    PLAN = "plan"
    APPLY = "apply"


class TeamWorkspaceVariablesPermission(Enum):
    """Team workspace permissions for variables"""
    NONE = "none"
    READ = "read"
    WRITE = "write"


class TeamWorkspaceStateVersionsPermissions(Enum):
    """Team workspace permissions for state versions"""

    NONE = "none"
    READ_OUTPUTS = "read-outputs"
    READ = "read"
    WRITE = "write"


class TeamWorkspaceSentinelMocksPermission(Enum):
    """Team workspace permissions for sentinel mocks"""

    NONE = "none"
    READ = "read"


class TeamWorkspaceAccess(Base, BaseObject):
    """Define team workspace access."""

    ID_PREFIX = "tws"

    __tablename__ = "team_workspace_access"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    team_id = sqlalchemy.Column(sqlalchemy.ForeignKey("team.id"), primary_key=True)
    team = sqlalchemy.orm.relationship("Team", back_populates="workspace_accesses")
    workspace_id = sqlalchemy.Column(sqlalchemy.ForeignKey("workspace.id"), primary_key=True)
    workspace = sqlalchemy.orm.relationship("Workspace", back_populates="team_accesses")

    access_type = sqlalchemy.Column(sqlalchemy.Enum(TeamWorkspaceAccessType))
    permission_runs = sqlalchemy.Column(sqlalchemy.Enum(TeamWorkspaceRunsPermission))
    permission_variables = sqlalchemy.Column(sqlalchemy.Enum(TeamWorkspaceVariablesPermission))
    permission_state_versions = sqlalchemy.Column(sqlalchemy.Enum(TeamWorkspaceStateVersionsPermissions))
    permission_sentinel_mocks = sqlalchemy.Column(sqlalchemy.Enum(TeamWorkspaceSentinelMocksPermission))
    permission_workspace_locking = sqlalchemy.Column(sqlalchemy.Boolean)
    permission_run_tasks = sqlalchemy.Column(sqlalchemy.Boolean)
