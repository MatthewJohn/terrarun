# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0


import sqlalchemy

from terrarun.database import Database
import terrarun.models.organisation
import terrarun.models.run_queue
import terrarun.models.agent
from terrarun.models.agent_pool_association import AgentPoolProjectAssociation, AgentPoolProjectPermission
import terrarun.models.apply
import terrarun.models.configuration
import terrarun.models.project
import terrarun.models.run
import terrarun.models.run_queue
import terrarun.models.workspace
import terrarun.terraform_command


class JobProcessor:

    @staticmethod
    def get_worker_job():
        """Get first run by type"""
        session = Database.get_session()
        run = None
        run_queue = session.query(
            terrarun.models.run_queue.RunQueue
        ).filter(
            terrarun.models.run_queue.RunQueue.agent_type==terrarun.models.run_queue.JobQueueAgentType.WORKER
        ).first()
        if run_queue:
            run = run_queue.run
            session.delete(run_queue)
            session.commit()
        return run

    @staticmethod
    def get_job_by_agent_and_job_types(agent: 'terrarun.models.agent.Agent', job_types):
        """Obtain list of jobs from queue that are applicable to an agent"""

        session = Database.get_session()
        query = session.query(
            terrarun.models.run_queue.RunQueue
        ).join(
            terrarun.models.run_queue.RunQueue.run
        ).join(
            terrarun.models.run.Run.configuration_version
        ).join(
            terrarun.models.configuration.ConfigurationVersion.workspace
        ).join(
            terrarun.models.workspace.Workspace.project
        ).join(
            terrarun.models.workspace.Workspace.organisation
        ).outerjoin(
            terrarun.models.organisation.Organisation.default_agent_pool
        ).outerjoin(
            AgentPoolProjectAssociation
        )

        # Filter jobs that are being handled by an agent
        query = query.filter(
            terrarun.models.run_queue.RunQueue.agent_type==terrarun.models.run_queue.JobQueueAgentType.AGENT,
            terrarun.models.run_queue.RunQueue.agent==None
        )

        # Limit by any organisations that have default agent pool and is set to this agent's pool
        # or don't have a default agent pool
        query = query.filter(sqlalchemy.or_(
            terrarun.models.organisation.Organisation.default_agent_pool==agent.agent_pool,
            terrarun.models.organisation.Organisation.default_agent_pool==None,
        ))

        if agent.agent_pool.organisation and agent.agent_pool.organisation_scoped:
            # Limit to organisation that this agent pool is tied to, ensuring
            # the default agent pool is None or this agent pool
            query = query.filter(
                terrarun.models.workspace.Workspace.organisation==agent.agent_pool.organisation,
            )
        elif agent.agent_pool.organisation is None:
            pass
        else:
            # Agent has organisation set, but is not organisation scoped.
            # Since we do not have any ways to associated agents to projects, environments or workspaces, give up
            # for now
            return None

        # Filter by allowed projects/workspaces, if not all workspaces are allowed
        # if not agent.agent_pool.organisation_scoped:
        #     allowed_projects = session.query(
        #         AgentPoolProjectPermission
        #     ).filter(
        #         AgentPoolProjectPermission.agent_pool==agent.agent_pool
        #     )
        #     query = query.filter(Workspace.project.in_(allowed_projects))

        # Filter any projects that have workers associated with them or this agent pool is associated with it
        # query = query.filter(sqlalchemy.or_(
        #     ~Project.agent_pool_associations.any(),
        #     AgentPoolProjectAssociation.agent_pool==agent.agent_pool
        # ))

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
        run = terrarun.models.run.Run.get_by_api_id(job_data.get("run_id"))
        if not run:
            return {}, 404

        # @TODO Handle error message
        plan_status = terrarun.terraform_command.TerraformCommandState(job_status.get("status"))
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
        if run.status == terrarun.models.run.RunStatus.CANCELED:
            # Unlock workspace
            run.unlock_workspace()
            return

        elif plan_status is terrarun.terraform_command.TerraformCommandState.RUNNING:
            run.update_status(terrarun.models.run.RunStatus.PLANNING)

        elif plan_status is terrarun.terraform_command.TerraformCommandState.ERRORED:
            run.update_status(terrarun.models.run.RunStatus.ERRORED)
            # Unlock workspace
            run.unlock_workspace()
            return

        elif plan_status is terrarun.terraform_command.TerraformCommandState.FINISHED:
            if run.plan_only or run.configuration_version.speculative or not run.plan.has_changes:
                run.update_status(terrarun.models.run.RunStatus.PLANNED_AND_FINISHED)
                # Unlock workspace
                run.unlock_workspace()
                return

            else:
                run.update_status(terrarun.models.run.RunStatus.PLANNED)
                terrarun.models.apply.Apply.create(plan=run.plan)

                # Queue worker job for next stages
                run.queue_worker_job()

        else:
            raise Exception(f"Unhandled plan status: {plan_status}")

    @classmethod
    def handle_apply_status_update(cls, job_status):
        """Handle status update for apply"""
        job_data = job_status.get("data")

        # Get plan ID from job status and update plan
        run = terrarun.models.run.Run.get_by_api_id(job_data.get("run_id"))
        if not run:
            return {}, 404

        # @TODO Handle error message
        apply_status = terrarun.terraform_command.TerraformCommandState(job_status.get("status"))
        # Update plan attributes
        run.plan.apply.update_attributes(
            status=apply_status
        )

        # Update run status
        ## Do not update run status if is has been cancelled
        if run.status == terrarun.models.run.RunStatus.CANCELED:
            # Unlock workspace
            run.unlock_workspace()
            return

        elif apply_status is terrarun.terraform_command.TerraformCommandState.RUNNING:
            run.update_status(terrarun.models.run.RunStatus.APPLYING)

        elif apply_status is terrarun.terraform_command.TerraformCommandState.ERRORED:
            run.update_status(terrarun.models.run.RunStatus.ERRORED)
            # Unlock workspace
            run.unlock_workspace()
            return

        elif apply_status is terrarun.terraform_command.TerraformCommandState.FINISHED:
            run.update_status(terrarun.models.run.RunStatus.APPLIED)
            # Unlock workspace
            run.unlock_workspace()

        else:
            raise Exception(f"Unhandled apply status: {apply_status}")
