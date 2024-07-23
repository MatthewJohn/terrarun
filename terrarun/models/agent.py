# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

from datetime import datetime
from typing import Optional
from enum import Enum
import os
import sqlalchemy
import sqlalchemy.orm

import terrarun.config
import terrarun.database
from terrarun.database import Base, Database
import terrarun.models.agent_pool
from terrarun.models.base_object import BaseObject
from terrarun.utils import generate_random_secret_string


class AgentStatus(Enum):
    """Status of agent"""

    IDLE = "idle"
    EXITED = "exited"
    ERRORED = "errored"
    UNKNOWN = "unknown"
    BUSY = "busy"


class Agent(Base, BaseObject):
    """DB model for an agent instance that can perform runs"""

    ID_PREFIX = "agent"

    __tablename__ = "agent"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    api_id_fk = sqlalchemy.Column(sqlalchemy.ForeignKey("api_id.id"), nullable=True)
    api_id_obj = sqlalchemy.orm.relation("ApiId", foreign_keys=[api_id_fk])

    name = sqlalchemy.Column(terrarun.database.Database.GeneralString, default=None)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=sqlalchemy.sql.func.now())

    # @TODO
    # Should this be held in the datbase?!
    status: Optional[AgentStatus] = sqlalchemy.Column(sqlalchemy.Enum(AgentStatus), default=None)
    last_ping_at: datetime = sqlalchemy.Column(sqlalchemy.DateTime, default=sqlalchemy.sql.func.now())

    agent_pool_id: Optional[int] = sqlalchemy.Column(sqlalchemy.ForeignKey("agent_pool.id"), nullable=True)
    agent_pool: Optional['terrarun.models.agent_pool.AgentPool'] = sqlalchemy.orm.relationship("AgentPool", back_populates="agents")

    token = sqlalchemy.Column(terrarun.database.Database.GeneralString)

    @classmethod
    def register_agent(cls, agent_token, name):
        """Register agent"""
        session = Database.get_session()

        # Create agent instance
        agent = cls(
            name=name,
            status=AgentStatus.IDLE,
            agent_pool=agent_token.agent_pool,
            token=generate_random_secret_string()
        )
        session.add(agent)

        # Update last used date of agent token
        agent_token.last_used_at = datetime.now()
        session.add(agent_token)

        session.commit()
        return agent

    @classmethod
    def get_by_id_and_token(cls, id, token):
        """Obtain agent object by ID and token value"""
        session = Database.get_session()
        return session.query(cls).filter(cls.id==id, cls.token==token).first()

    @classmethod
    def get_by_agent_pool_and_api_id(cls, agent_pool, api_id):
        """Get agent by API ID and agent pool"""
        session = Database.get_session()
        return session.query(cls).filter(
            cls.agent_pool==agent_pool, cls.id==cls.db_id_from_api_id(api_id)
        ).first()

    def update_status(self, new_status):
        """Update status of agent"""
        session = Database.get_session()
        self.status = new_status
        self.last_ping_at = datetime.now()
        session.add(self)
        session.commit()
