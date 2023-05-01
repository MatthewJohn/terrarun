# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from enum import Enum
import sqlalchemy
import sqlalchemy.orm

from terrarun.models.base_object import BaseObject
from terrarun.database import Base, Database


class RunQueueType(Enum):
    WORKER = "WORKER"
    AGENT = "AGENT"


class RunQueue(Base, BaseObject):

    ID_PREFIX = 'rq'

    __tablename__ = 'run_queue'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    run_id = sqlalchemy.Column(sqlalchemy.ForeignKey("run.id"), nullable=False)
    run = sqlalchemy.orm.relation("Run", back_populates="run_queue")

    job_type = sqlalchemy.Column(sqlalchemy.Enum(RunQueueType))

    @classmethod
    def get_job_by_type(cls, type_):
        """Get first run by type"""
        session = Database.get_session()
        return session.query(cls).filter(cls.job_type==type_).first()
