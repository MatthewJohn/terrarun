
import sqlalchemy
import sqlalchemy.orm

from terrarun.base_object import BaseObject
from terrarun.database import Base, Database


class RunQueue(Base, BaseObject):

    ID_PREFIX = 'rq'

    __tablename__ = 'run_queue'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    run_id = sqlalchemy.Column(sqlalchemy.ForeignKey("run.id"), nullable=False)
    run = sqlalchemy.orm.relation("Run", back_populates="run_queue")

    @classmethod
    def queue_run(cls, run):
        """Queue a run to be executed."""
        session = Database.get_session()
        run_queue = cls(run=run)
        session.add(run_queue)
        session.commit()