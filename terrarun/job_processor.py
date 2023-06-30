
import sqlalchemy

from terrarun.database import Database
from terrarun import RunQueue
from terrarun.models.agent_pool_association import AgentPoolProjectAssociation, AgentPoolProjectPermission
from terrarun.models.apply import Apply
from terrarun.models.configuration import ConfigurationVersion
from terrarun.models.project import Project
from terrarun.models.run import Run, RunStatus
from terrarun.models.run_queue import JobQueueAgentType
from terrarun.models.workspace import Workspace
from terrarun.terraform_command import TerraformCommandState


class JobProcessor:

    @staticmethod
    def get_worker_job():
        """Get first run by type"""
        session = Database.get_session()
        run = None
        run_queue = session.query(RunQueue).filter(RunQueue.agent_type==JobQueueAgentType.WORKER).first()
        if run_queue:
            run = run_queue.run
            session.delete(run_queue)
            session.commit()
        return run

    @staticmethod
    def get_job_by_agent_and_job_types(agent, job_types):
        """Obtain list of jobs from queue that are applicable to an agent"""

        session = Database.get_session()
        query = session.query(RunQueue).join(Run).join(ConfigurationVersion).join(Workspace).join(Project).outerjoin(AgentPoolProjectAssociation)

        # Filter jobs that are being handled by an agent
        query = query.filter(RunQueue.agent==None)

        # If agent pool is tied to an organisation, limit to just the organisation
        if agent.agent_pool.organisation:
            query = query.filter(RunQueue.run.configuration_version.workspace.organisation==agent.agent_pool.organisation)

        # Filter by allowed projects/workspaces, if not all workspaces are allowed
        if not agent.agent_pool.allow_all_workspaces:
            allowed_projects = session.query(
                AgentPoolProjectPermission
            ).filter(
                AgentPoolProjectPermission.agent_pool==agent.agent_pool
            )
            query = query.filter(Workspace.project.in_(allowed_projects))

        # Filter any projects that have workers associated with them or this agent pool is associated with it
        query = query.filter(sqlalchemy.or_(
            ~Project.agent_pool_associations.any(),
            AgentPoolProjectAssociation.agent_pool==agent.agent_pool
        ))

        # @TODO Filter by environment if there are any within the organisation for the agent pool

        # @TODO Filter by job type

        # Set to with_for_updates to lock row, avoiding any other requests taking the plan
        query = query.with_for_update()

        job = query.first()
        # Add agent to row, if one has been returned
        if job:
            job.agent = agent
            session.add(job)
            session.commit()

        return job

    @classmethod
    def handle_plan_status_update(self, job_status):
        """Handle status update for plan"""

        job_data = job_status.get("data")

        # Get plan ID from job status and update plan
        run = Run.get_by_api_id(job_data.get("run_id"))
        if not run:
            return {}, 404

        # @TODO Handle error message
        plan_status = TerraformCommandState(job_status.get("status"))
        # Update plan attributes
        run.plan.update_attributes(
            status=plan_status,
            has_changes=job_data.get("has_changes"),
            resource_additions=job_data.get("resource_additions"),
            resource_changes=job_data.get("resource_changes"),
            resource_destructions=job_data.get("resource_destructions"),
        )

        # Update run status
        ## Do not update run status if is has been cancelled
        if run.status == RunStatus.CANCELED:
            return

        elif plan_status is TerraformCommandState.RUNNING:
            run.update_status(RunStatus.PLANNING)

        elif plan_status is TerraformCommandState.ERRORED:
            run.update_status(RunStatus.ERRORED)
            return

        elif plan_status is TerraformCommandState.FINISHED:
            if run.plan_only or run.configuration_version.speculative or not run.plan.has_changes:
                run.update_status(RunStatus.PLANNED_AND_FINISHED)
                return

            else:
                run.update_status(RunStatus.PLANNED)
                Apply.create(plan=run.plan)

                # Queue worker job for next stages
                run.queue_worker_job()

        else:
            raise Exception(f"Unhandled plan status: {plan_status}")



    @classmethod
    def handle_apply_status_update(cls, job_status):
        """Handle status update for apply"""
        job_data = job_status.get("data")

        # Get plan ID from job status and update plan
        run = Run.get_by_api_id(job_data.get("run_id"))
        if not run:
            return {}, 404

        # @TODO Handle error message
        apply_status = TerraformCommandState(job_status.get("status"))
        # Update plan attributes
        run.plan.apply.update_attributes(
            status=apply_status
        )

        # Update run status
        ## Do not update run status if is has been cancelled
        if run.status == RunStatus.CANCELED:
            return

        elif apply_status is TerraformCommandState.RUNNING:
            run.update_status(RunStatus.APPLYING)

        elif apply_status is TerraformCommandState.ERRORED:
            run.update_status(RunStatus.ERRORED)
            return

        elif apply_status is TerraformCommandState.FINISHED:
            run.update_status(RunStatus.APPLIED)
            # Queue worker job to process state
            run.queue_worker_job()

        else:
            raise Exception(f"Unhandled apply status: {apply_status}")
