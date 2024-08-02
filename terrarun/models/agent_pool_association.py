# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

import sqlalchemy
import sqlalchemy.orm

from terrarun.database import Base
import terrarun.models.environment
import terrarun.models.lifecycle


# @TODO These are currently unused

class AgentPoolProjectPermission(Base):
    """
    Define agent pool project permission.

    This is only used when assigning a project to an agent pool.
    """

    __tablename__ = "agent_pool_project_permission"

    agent_pool_id = sqlalchemy.Column(sqlalchemy.ForeignKey("agent_pool.id"), nullable=False, primary_key=True)
    agent_pool = sqlalchemy.orm.relationship("AgentPool", foreign_keys=[agent_pool_id])

    project_id = sqlalchemy.Column(sqlalchemy.ForeignKey("project.id"), nullable=False, primary_key=True)
    project = sqlalchemy.orm.relationship("Project", foreign_keys=[project_id], back_populates="agent_pool_permissions")


class AgentPoolWorkspacePermission(Base):
    """
    Define agent pool workspace permission.

    This is only used when assigning a workspace to an agent pool.
    """

    __tablename__ = "agent_pool_workspace_permission"

    agent_pool_id = sqlalchemy.Column(sqlalchemy.ForeignKey("agent_pool.id"), nullable=False, primary_key=True)
    agent_pool = sqlalchemy.orm.relationship("AgentPool", foreign_keys=[agent_pool_id])

    workspace_id = sqlalchemy.Column(sqlalchemy.ForeignKey("project.id"), nullable=False, primary_key=True)
    workspace = sqlalchemy.orm.relationship("Workspace", foreign_keys=[workspace_id], back_populates="agent_pool_permissions")
