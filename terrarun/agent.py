# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential


from datetime import datetime
from enum import Enum
import os
import sqlalchemy
import sqlalchemy.orm

import terrarun.config
import terrarun.database
from terrarun.database import Base, Database
from terrarun.base_object import BaseObject


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
    name = sqlalchemy.Column(terrarun.database.Database.GeneralString, default=None)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=sqlalchemy.sql.func.now())

    # @TODO
    # Should this be held in the datbase?!
    status = sqlalchemy.Column(sqlalchemy.Enum(AgentStatus), default=None)
    last_ping_at = sqlalchemy.Column(sqlalchemy.DateTime, default=sqlalchemy.sql.func.now())

    agent_pool_id = sqlalchemy.Column(sqlalchemy.ForeignKey("agent_pool.id"), nullable=True)
    agent_pool = sqlalchemy.orm.relationship("AgentPool", back_populates="agents")

    @classmethod
    def register_agent(cls, agent_token, name):
        """Register agent"""
        session = Database.get_session()

        # Create agent instance
        agent = cls(name=name, status=AgentStatus.IDLE, agent_pool=agent_token.agent_pool)
        session.add(agent)

        # Update last used date of agent token
        agent_token.last_used_at = datetime.now()
        session.add(agent_token)

        session.commit()
        return agent
