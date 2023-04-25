# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import sqlalchemy
import sqlalchemy.orm

from terrarun.database import Base
import terrarun.environment
import terrarun.lifecycle


class AgentPoolWorkspacePermission(Base):
    """Define agent pool workspace permission."""

    __tablename__ = "agent_pool_workspace_permission"

    agent_pool_id = sqlalchemy.Column(sqlalchemy.ForeignKey("agent_pool.id"), nullable=False, primary_key=True)
    agent_pool = sqlalchemy.orm.relation("AgentPool", foreign_keys=[agent_pool_id])

    workspace_id = sqlalchemy.Column(sqlalchemy.ForeignKey("workspace.id"), nullable=False, primary_key=True)
    workspace = sqlalchemy.orm.relation("Workspace", foreign_keys=[workspace_id])


class AgentPoolWorkspaceAssociation(Base):
    """Define agent pool workspace associations."""

    __tablename__ = "agent_pool_workspace_association"

    agent_pool_id = sqlalchemy.Column(sqlalchemy.ForeignKey("agent_pool.id"), nullable=False, primary_key=True)
    agent_pool = sqlalchemy.orm.relation("AgentPool", foreign_keys=[agent_pool_id])

    workspace_id = sqlalchemy.Column(sqlalchemy.ForeignKey("workspace.id"), nullable=False, primary_key=True)
    workspace = sqlalchemy.orm.relation("Workspace", foreign_keys=[workspace_id])


class AgentPoolEnvironmentAssociation(Base):
    """Define agent pool environment associations."""

    __tablename__ = "agent_pool_environment_association"

    agent_pool_id = sqlalchemy.Column(sqlalchemy.ForeignKey("agent_pool.id"), nullable=False, primary_key=True)
    agent_pool = sqlalchemy.orm.relation("AgentPool", foreign_keys=[agent_pool_id])

    environment_id = sqlalchemy.Column(sqlalchemy.ForeignKey("environment.id"), nullable=False, primary_key=True)
    environment = sqlalchemy.orm.relation("Environment", foreign_keys=[environment_id])
