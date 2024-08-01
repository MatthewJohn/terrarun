# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

from enum import Enum
from typing import Optional
import sqlalchemy
import sqlalchemy.orm

from terrarun.models.base_object import BaseObject
from terrarun.database import Base, Database
import terrarun.models.run
import terrarun.models.api_id
import terrarun.models.agent
import terrarun.models.user_token


class JobQueueAgentType(Enum):
    WORKER = "WORKER"
    AGENT = "AGENT"


class JobQueueType(Enum):

    PLAN = "plan"
    APPLY = "apply"
    POLICY = "policy"
    ASSESSMENT = "assessment"
    TEST = "test"


class RunQueue(Base, BaseObject):

    ID_PREFIX = 'job'

    __tablename__ = 'run_queue'

    id: int = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    api_id_fk: int = sqlalchemy.Column(sqlalchemy.ForeignKey("api_id.id"), nullable=True)
    api_id_obj: 'terrarun.models.api_id.ApiId' = sqlalchemy.orm.relation("ApiId", foreign_keys=[api_id_fk])

    run_id: int = sqlalchemy.Column(sqlalchemy.ForeignKey("run.id"), nullable=False)
    run: 'terrarun.models.run.Run' = sqlalchemy.orm.relation("Run", back_populates="run_queue")

    agent_type: JobQueueAgentType = sqlalchemy.Column(sqlalchemy.Enum(JobQueueAgentType))
    job_type: JobQueueType = sqlalchemy.Column(sqlalchemy.Enum(JobQueueType))

    agent_id: Optional[int] = sqlalchemy.Column(sqlalchemy.ForeignKey("agent.id"), nullable=True)
    agent: Optional['terrarun.models.agent.Agent'] = sqlalchemy.orm.relation("Agent")

    user_token: Optional['terrarun.models.user_token.UserToken'] = sqlalchemy.orm.relationship("UserToken", uselist=False, backref="job")
