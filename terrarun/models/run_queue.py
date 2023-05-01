# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from enum import Enum
import sqlalchemy
import sqlalchemy.orm
from terrarun.models.agent_pool_association import AgentPoolEnvironmentAssociation, AgentPoolProjectAssociation, AgentPoolProjectPermission

from terrarun.models.base_object import BaseObject
from terrarun.database import Base, Database


class JobQueueAgentType(Enum):
    WORKER = "WORKER"
    AGENT = "AGENT"


class JobQueueType(Enum):

    PLAN = "plan"
    APPLY = "apply"
    POLICY = "policy"
    ASSESSMENT = "assessment"


class RunQueue(Base, BaseObject):

    ID_PREFIX = 'job'

    __tablename__ = 'run_queue'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    run_id = sqlalchemy.Column(sqlalchemy.ForeignKey("run.id"), nullable=False)
    run = sqlalchemy.orm.relation("Run", back_populates="run_queue")

    agent_type = sqlalchemy.Column(sqlalchemy.Enum(JobQueueAgentType))
    job_type = sqlalchemy.Column(sqlalchemy.Enum(JobQueueType))

    agent_id = sqlalchemy.Column(sqlalchemy.ForeignKey("agent.id"), nullable=True)
    agent = sqlalchemy.orm.relation("Agent")

    user_token = sqlalchemy.orm.relationship("UserToken", uselist=False, backref="job")
