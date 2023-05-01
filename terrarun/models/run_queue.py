# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from enum import Enum
import sqlalchemy
import sqlalchemy.orm
from terrarun.models.agent_pool_association import AgentPoolEnvironmentAssociation, AgentPoolProjectPermission

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

    ID_PREFIX = 'rq'

    __tablename__ = 'run_queue'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    run_id = sqlalchemy.Column(sqlalchemy.ForeignKey("run.id"), nullable=False)
    run = sqlalchemy.orm.relation("Run", back_populates="run_queue")

    agent_type = sqlalchemy.Column(sqlalchemy.Enum(JobQueueAgentType))
    job_type = sqlalchemy.Column(sqlalchemy.Enum(JobQueueType))

    @classmethod
    def get_job_by_type(cls, type_):
        """Get first run by type"""
        session = Database.get_session()
        run = None
        run_queue = session.query(cls).filter(cls.agent_type==type_).first()
        if run_queue:
            run = run_queue.run
            session.delete(run_queue)
            session.commit()
        return run

    @classmethod
    def get_job_by_agent_and_job_types(cls, agent, job_types):
        """Obtain list of jobs from queue that are applicable to an agent"""

        # class AgentPoolProjectAssociation(Base):
        #     """Define agent pool project associations."""

        #     __tablename__ = "agent_pool_project_association"

        #     agent_pool_id = sqlalchemy.Column(sqlalchemy.ForeignKey("agent_pool.id"), nullable=False, primary_key=True)
        #     agent_pool = sqlalchemy.orm.relation("AgentPool", foreign_keys=[agent_pool_id])

        #     project_id = sqlalchemy.Column(sqlalchemy.ForeignKey("project.id"), nullable=False, primary_key=True)
        #     project = sqlalchemy.orm.relation("Project", foreign_keys=[project_id])


        # class AgentPoolEnvironmentAssociation(Base):

        session = Database.get_session()
        query = session.query(cls)
        # If agent pool is tied to an organisation, limit to just the organisation
        if agent.agent_pool.organisation:
            query = query.filter(cls.run.configuration_version.workspace.organisation==agent.agent_pool.organisation)

        # Filter by allowed projects/workspaces, if not all workspaces are allowed
        if not agent.agent_pool.allow_all_workspaces:
            allowed_projects = session.query(
                AgentPoolProjectPermission
            ).filter(
                AgentPoolProjectPermission.agent_pool==agent.agent_pool
            )
            query = query.filter(cls.run.configuration_version.workspace.project.in_(allowed_projects))

        # Filter any projects that have workers associated with them
        query = query.filter(cls.run.configuration_version.workspace.project)
