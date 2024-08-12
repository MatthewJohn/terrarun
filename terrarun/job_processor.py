# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

from typing import Tuple, Optional

import sqlalchemy

from terrarun.database import Database
import terrarun.models.organisation
import terrarun.models.agent
import terrarun.models.apply
import terrarun.models.configuration
import terrarun.models.project
import terrarun.models.run
import terrarun.models.run_flow
import terrarun.models.run_queue
import terrarun.models.workspace
import terrarun.models.environment
import terrarun.terraform_command
import terrarun.workspace_execution_mode


class JobProcessor:

    @staticmethod
    def get_worker_job() -> Optional['terrarun.models.run.Run']:
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
    def get_job_by_agent_and_job_types(agent: 'terrarun.models.agent.Agent', job_types) -> Tuple['terrarun.models.run_queue.RunQueue', 'terrarun.workspace_execution_mode.WorkspaceExecutionMode']:
        """
        Obtain list of jobs from queue that are applicable to an agent

        Returns job and execution mode used for query.

        @TODO Add support for job_types
        """

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
            terrarun.models.workspace.Workspace.environment
        ).join(
            terrarun.models.workspace.Workspace.organisation
        ).outerjoin(
            terrarun.models.organisation.Organisation.default_agent_pool
        )

        # Filter jobs that are being handled by an agent
        query = query.filter(
            terrarun.models.run_queue.RunQueue.agent_type==terrarun.models.run_queue.JobQueueAgentType.AGENT,
            terrarun.models.run_queue.RunQueue.agent==None
        )

        execution_mode = None

        # If current agent is not assigned to an organisation, look for
        # any jobs with execution type of "remote"
        if agent.agent_pool.organisation is None:
            execution_mode = terrarun.workspace_execution_mode.WorkspaceExecutionMode.REMOTE
            query = query.filter(sqlalchemy.or_(
                sqlalchemy.and_(
                    terrarun.models.workspace.Workspace._execution_mode==execution_mode,
                ).self_group(),
                sqlalchemy.and_(
                    terrarun.models.workspace.Workspace._execution_mode==None,
                    terrarun.models.project.Project._execution_mode==execution_mode,
                ).self_group(),
                sqlalchemy.and_(
                    terrarun.models.workspace.Workspace._execution_mode==None,
                    terrarun.models.project.Project._execution_mode==None,
                    terrarun.models.organisation.Organisation.default_execution_mode==execution_mode,
                ).self_group(),
            ))
        else:
            execution_mode = terrarun.workspace_execution_mode.WorkspaceExecutionMode.AGENT

            # Limit to organisation that this agent pool is tied to, ensuring
            # the default agent pool is None or this agent pool
            query = query.filter(
                terrarun.models.workspace.Workspace.organisation==agent.agent_pool.organisation,
            )

            # Limit by execution type of agent
            query = query.filter(sqlalchemy.or_(
                sqlalchemy.and_(
                    terrarun.models.workspace.Workspace._execution_mode==execution_mode,
                ).self_group(),
                sqlalchemy.and_(
                    terrarun.models.workspace.Workspace._execution_mode==None,
                    terrarun.models.project.Project._execution_mode==execution_mode,
                ).self_group(),
                sqlalchemy.and_(
                    terrarun.models.workspace.Workspace._execution_mode==None,
                    terrarun.models.project.Project._execution_mode==None,
                    terrarun.models.organisation.Organisation.default_execution_mode==execution_mode,
                ).self_group(),
            ))

            if agent.agent_pool.organisation_scoped:
                # Limit by any workspace, project or environment that has the agent pool assigned
                query = query.filter(sqlalchemy.or_(
                    # If workspace is assigned to agent pool
                    sqlalchemy.and_(
                        terrarun.models.workspace.Workspace.agent_pool==agent.agent_pool,
                    ).self_group(),
                    # Or workspace is unassigned and project is assigned to agent pool
                    sqlalchemy.and_(
                        terrarun.models.workspace.Workspace.agent_pool==None,
                        terrarun.models.project.Project.default_agent_pool==agent.agent_pool,
                    ).self_group(),
                    # Or assigned at environment
                    sqlalchemy.and_(
                        terrarun.models.workspace.Workspace.agent_pool==None,
                        terrarun.models.project.Project.default_agent_pool==None,
                        terrarun.models.environment.Environment.default_agent_pool==agent.agent_pool,
                    ).self_group(),
                    # Or assigned at org
                    sqlalchemy.and_(
                        terrarun.models.workspace.Workspace.agent_pool==None,
                        terrarun.models.project.Project.default_agent_pool==None,
                        terrarun.models.environment.Environment.default_agent_pool==None,
                        terrarun.models.organisation.Organisation.default_agent_pool==agent.agent_pool,
                    ).self_group(),
                ))
            else:
                # Allow non-scoped agent pools to pick up jobs for workspaces
                # that don't have an agent pool associated
                # @TODO Verify this - should these be allowed at all?
                query = query.filter(
                    terrarun.models.workspace.Workspace.agent_pool==None,
                    terrarun.models.project.Project.default_agent_pool==None,
                    terrarun.models.environment.Environment.default_agent_pool==None,
                    terrarun.models.organisation.Organisation.default_agent_pool==None,
                )

        # Set to with_for_updates to lock row, avoiding any other requests taking the plan
        query = query.with_for_update()

        job: Optional['terrarun.models.run_queue.RunQueue'] = query.first()
        # Add agent to row, if one has been returned
        if job:
            job.agent = agent
            session.add(job)
            session.commit()

        return job, execution_mode

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
        if run.status == terrarun.models.run_flow.RunStatus.CANCELED:
            # Unlock workspace
            run.unlock_workspace()
            return

        elif plan_status is terrarun.terraform_command.TerraformCommandState.RUNNING:
            run.update_status(terrarun.models.run_flow.RunStatus.PLANNING)

        elif plan_status is terrarun.terraform_command.TerraformCommandState.ERRORED:
            run.update_status(terrarun.models.run_flow.RunStatus.ERRORED)
            # Unlock workspace
            run.unlock_workspace()
            return

        elif plan_status is terrarun.terraform_command.TerraformCommandState.FINISHED:
            if run.plan_only or run.configuration_version.speculative or not run.plan.has_changes:
                run.update_status(terrarun.models.run_flow.RunStatus.PLANNED_AND_FINISHED)
                # Unlock workspace
                run.unlock_workspace()
                return

            else:
                run.update_status(terrarun.models.run_flow.RunStatus.PLANNED)
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
        if run.status == terrarun.models.run_flow.RunStatus.CANCELED:
            # Unlock workspace
            run.unlock_workspace()
            return

        elif apply_status is terrarun.terraform_command.TerraformCommandState.RUNNING:
            run.update_status(terrarun.models.run_flow.RunStatus.APPLYING)

        elif apply_status is terrarun.terraform_command.TerraformCommandState.ERRORED:
            run.update_status(terrarun.models.run_flow.RunStatus.ERRORED)
            # Unlock workspace
            run.unlock_workspace()
            return

        elif apply_status is terrarun.terraform_command.TerraformCommandState.FINISHED:
            run.update_status(terrarun.models.run_flow.RunStatus.APPLIED)
            # Unlock workspace
            run.unlock_workspace()

        else:
            raise Exception(f"Unhandled apply status: {apply_status}")
