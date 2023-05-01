# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import sqlalchemy
import sqlalchemy.orm

from terrarun.database import Base
import terrarun.models.environment
import terrarun.models.lifecycle


class AgentPoolProjectPermission(Base):
    """Define agent pool project permission."""

    __tablename__ = "agent_pool_project_permission"

    agent_pool_id = sqlalchemy.Column(sqlalchemy.ForeignKey("agent_pool.id"), nullable=False, primary_key=True)
    agent_pool = sqlalchemy.orm.relation("AgentPool", foreign_keys=[agent_pool_id])

    project_id = sqlalchemy.Column(sqlalchemy.ForeignKey("project.id"), nullable=False, primary_key=True)
    project = sqlalchemy.orm.relationship("Project", foreign_keys=[project_id], back_populates="agent_pool_permissions")


class AgentPoolProjectAssociation(Base):
    """Define agent pool project associations."""

    __tablename__ = "agent_pool_project_association"

    agent_pool_id = sqlalchemy.Column(sqlalchemy.ForeignKey("agent_pool.id"), nullable=False, primary_key=True)
    agent_pool = sqlalchemy.orm.relation("AgentPool", foreign_keys=[agent_pool_id])

    project_id = sqlalchemy.Column(sqlalchemy.ForeignKey("project.id"), nullable=False, primary_key=True)
    project = sqlalchemy.orm.relationship("Project", foreign_keys=[project_id], back_populates="agent_pool_associations")


class AgentPoolEnvironmentAssociation(Base):
    """Define agent pool environment associations."""

    __tablename__ = "agent_pool_environment_association"

    agent_pool_id = sqlalchemy.Column(sqlalchemy.ForeignKey("agent_pool.id"), nullable=False, primary_key=True)
    agent_pool = sqlalchemy.orm.relation("AgentPool", foreign_keys=[agent_pool_id])

    environment_id = sqlalchemy.Column(sqlalchemy.ForeignKey("environment.id"), nullable=False, primary_key=True)
    environment = sqlalchemy.orm.relation("Environment", foreign_keys=[environment_id])
