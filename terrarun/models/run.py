# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from enum import Enum
import json
import os
import datetime

import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.sql
from terrarun.api_request import ApiRequest
from terrarun.errors import FailedToUnlockWorkspaceError, RunCannotBeDiscardedError
from terrarun.models.audit_event import AuditEvent, AuditEventType

from terrarun.database import Base, Database
import terrarun.database
import terrarun.models.plan
import terrarun.models.apply
import terrarun.models.state_version
from terrarun.models.run_queue import JobQueueType, RunQueue, JobQueueAgentType
from terrarun.models.task_result import TaskResultStatus
from terrarun.models.task_stage import TaskStage, TaskStageStatus
import terrarun.terraform_command
from terrarun.models.base_object import BaseObject
import terrarun.utils
import terrarun.config
from terrarun.models.workspace_task import WorkspaceTaskEnforcementLevel, WorkspaceTaskStage


class RunStatus(Enum):

    PENDING = 'pending'
    FETCHING = 'fetching'
    FETCHING_COMPLETED = 'fetching_completed'
    PRE_PLAN_RUNNING = 'pre_plan_running'
    PRE_PLAN_COMPLETED = 'pre_plan_completed'
    QUEUING = 'queuing'
    PLAN_QUEUED = 'plan_queued'
    PLANNING = 'planning'
    PLANNED = 'planned'
    COST_ESTIMATING = 'cost_estimating'
    COST_ESTIMATED = 'cost_estimated'
    POLICY_CHECKING = 'policy_checking'
    POLICY_OVERRIDE = 'policy_override'
    POLICY_SOFT_FAILED = 'policy_soft_failed'
    POLICY_CHECKED = 'policy_checked'
    CONFIRMED = 'confirmed'
    POST_PLAN_RUNNING = 'post_plan_running'
    POST_PLAN_COMPLETED = 'post_plan_completed'
    PLANNED_AND_FINISHED = 'planned_and_finished'
    PRE_APPLY_RUNNING = 'pre_apply_running'  # Not yet part of official documentation
    PRE_APPLY_COMPLETED = 'pre_apply_completed'  # Not yet part of official documentation
    APPLY_QUEUED = 'apply_queued'
    APPLYING = 'applying'
    APPLIED = 'applied'
    DISCARDED = 'discarded'
    ERRORED = 'errored'
    CANCELED = 'canceled'
    FORCE_CANCELLED = 'force_canceled'


class RunOperations:

    PLAN_ONLY = 'plan_only'
    PLAN_AND_APPLY = 'plan_and_apply'
    REFRESH_ONLY = 'refresh_only'
    DESTROY = 'destroy'
    EMPTY_APPLY = 'empty_apply'


class Run(Base, BaseObject):

    ID_PREFIX = 'run'

    __tablename__ = 'run'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    api_id_fk = sqlalchemy.Column(sqlalchemy.ForeignKey("api_id.id"), nullable=True)
    api_id_obj = sqlalchemy.orm.relation("ApiId", foreign_keys=[api_id_fk])

    configuration_version_id = sqlalchemy.Column(sqlalchemy.ForeignKey("configuration_version.id"), nullable=False)
    configuration_version = sqlalchemy.orm.relationship("ConfigurationVersion", back_populates="runs")

    state_versions = sqlalchemy.orm.relation("StateVersion", back_populates="run")
    plans = sqlalchemy.orm.relation("Plan", back_populates="run")

    run_queue = sqlalchemy.orm.relation("RunQueue", back_populates="run", uselist=False)

    status = sqlalchemy.Column(sqlalchemy.Enum(RunStatus))
    confirmed = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    auto_apply = sqlalchemy.Column(sqlalchemy.Boolean)
    message = sqlalchemy.Column(terrarun.database.Database.GeneralString)
    plan_only = sqlalchemy.Column(sqlalchemy.Boolean)
    refresh = sqlalchemy.Column(sqlalchemy.Boolean)
    refresh_only = sqlalchemy.Column(sqlalchemy.Boolean)
    is_destroy = sqlalchemy.Column(sqlalchemy.Boolean)
    _replace_addrs = sqlalchemy.Column("replace_addrs", terrarun.database.Database.GeneralString)
    _target_addrs = sqlalchemy.Column("target_addrs", terrarun.database.Database.GeneralString)
    _variables = sqlalchemy.Column("variables", terrarun.database.Database.GeneralString)
    tool_id = sqlalchemy.Column(sqlalchemy.ForeignKey("tool.id"), nullable=True)
    tool = sqlalchemy.orm.relationship("Tool")
    allow_empty_apply = sqlalchemy.Column(sqlalchemy.Boolean)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=sqlalchemy.sql.func.now())

    created_by_id = sqlalchemy.Column(sqlalchemy.ForeignKey("user.id", name="run_created_by_id_user_id"), nullable=True)
    created_by = sqlalchemy.orm.relation("User", foreign_keys=[created_by_id])

    task_stages = sqlalchemy.orm.relationship("TaskStage", back_populates="run")

    @property
    def replace_addrs(self):
        if not self._replace_addrs:
            return []
        return json.loads(self._replace_addrs)

    @replace_addrs.setter
    def replace_addrs(self, value):
        self._replace_addrs = json.dumps(value)

    @property
    def target_addrs(self):
        if not self._target_addrs:
            return []
        return json.loads(self._target_addrs)

    @target_addrs.setter
    def target_addrs(self, value):
        self._target_addrs = json.dumps(value)

    @property
    def variables(self):
        return json.loads(self._variables)

    @variables.setter
    def variables(self, value):
        self._variables = json.dumps(value)

    @classmethod
    def create(cls, configuration_version, created_by, message, **attributes):
        """Create run and return instance."""
        session = Database.get_session()

        if configuration_version.workspace.tool is None:
            raise Exception('Terraform version must be configured in project/workspace')

        if ((tool := attributes.get('tool')) and
                tool != configuration_version.workspace.tool and
                not attributes.get('plan_only')):
            raise Exception('Custom Terraform version cannot be used for non-refresh-only runs')


        # Check rules for environment to ensure that environment can create a run
        if not configuration_version.can_create_run():
            raise Exception("Run cannot be created due to lifecycle rules")

        run = Run(
            configuration_version=configuration_version,
            created_by=created_by,
            message=message,
            **attributes)
        session.add(run)

        session.commit()
        session.refresh(run)
        run.update_status(RunStatus.PENDING, current_user=created_by)

        # Create all task stages
        TaskStage.create(
            run=run,
            stage=WorkspaceTaskStage.PRE_PLAN,
            workspace_tasks=run.pre_plan_workspace_tasks)
        TaskStage.create(
            run=run,
            stage=WorkspaceTaskStage.POST_PLAN,
            workspace_tasks=run.post_plan_workspace_tasks)
        TaskStage.create(
            run=run,
            stage=WorkspaceTaskStage.PRE_APPLY,
            workspace_tasks=run.pre_apply_workspace_tasks)

        # if not configuration_version.workspace.lock(reason=message, run=run, session=session):
        #     session.rollback()
        #     raise Exception("Workspace is already locked")

        # Queue to be processed
        run.queue_worker_job()
        return run

    def cancel(self, user):
        """Cancel run"""
        self.update_status(RunStatus.CANCELED, current_user=user)

    def discard(self, user):
        """Discard run"""
        if self.status is not RunStatus.POST_PLAN_COMPLETED:
            raise RunCannotBeDiscardedError("Run is not in a state that can be discarded")
        if not self.configuration_version.workspace.unlock(run=self):
            raise FailedToUnlockWorkspaceError("Failed to unlock run")
        self.update_status(RunStatus.DISCARDED)

    @property
    def pre_plan_workspace_tasks(self):
        """Return list of workspace tasks for pre-plan"""
        return [
            workspace_task
            for workspace_task in self.configuration_version.workspace.workspace_tasks
            if workspace_task.stage == WorkspaceTaskStage.PRE_PLAN and workspace_task.active
        ]

    @property
    def post_plan_workspace_tasks(self):
        """Return list of workspace tasks for post-plan"""
        return [
            workspace_task
            for workspace_task in self.configuration_version.workspace.workspace_tasks
            if workspace_task.stage == WorkspaceTaskStage.POST_PLAN and workspace_task.active
        ]

    @property
    def pre_apply_workspace_tasks(self):
        """Return list of workspace tasks for pre-apply"""
        return [
            workspace_task
            for workspace_task in self.configuration_version.workspace.workspace_tasks
            if workspace_task.stage == WorkspaceTaskStage.PRE_APPLY and workspace_task.active
        ]

    def handling_pending(self):
        """Create plan and setup pre-plan tasks"""
        # Create plan, as the terraform client expects this
        # to immediately exist
        terrarun.models.plan.Plan.create(run=self)
        self.update_status(RunStatus.PRE_PLAN_RUNNING)

        # Handle pre-run tasks.
        if self.pre_plan_workspace_tasks:
            task_stage = [task_stage for task_stage in self.task_stages if task_stage.stage is WorkspaceTaskStage.PRE_PLAN][0]

            # Iterate over task results and execute
            for task_result in task_stage.task_results:
                task_result.execute()

        # Queue plan
        self.queue_worker_job()

    def handle_pre_plan_running(self):
        """Hanlde pre-plan running, waiting for task stages to complete"""
        task_stages = [task_stage for task_stage in self.task_stages if task_stage.stage is WorkspaceTaskStage.PRE_PLAN]

        should_continue = True
        completed = True
        if len(task_stages) == 0:
            # No task stages - no tasks available
            pass
        elif len(task_stages) == 1:
            task_stage = task_stages[0]
            should_continue, completed = task_stage.check_status()

        if should_continue:
            if completed:
                self.update_status(RunStatus.PRE_PLAN_COMPLETED)
            self.queue_worker_job()

    def execute_plan(self):
        """Execute plan"""
        session = Database.get_session()
        self.update_status(RunStatus.PLANNING)
        plan = self.plan
        self.plan.execute()
        session.refresh(self)
        if self.status == RunStatus.CANCELED:
            return
        elif plan.status is terrarun.terraform_command.TerraformCommandState.ERRORED:
            self.update_status(RunStatus.ERRORED)
            return
        elif self.plan_only or self.configuration_version.speculative or not self.plan.has_changes:
            self.update_status(RunStatus.PLANNED_AND_FINISHED)
            return
        else:
            self.update_status(RunStatus.PLANNED)
            terrarun.models.apply.Apply.create(plan=self.plan)
            self.queue_worker_job()

    def handle_planned(self):
        """Handle planned state"""
        # If successfully planned, move to pre-plan tasks
        self.update_status(RunStatus.POST_PLAN_RUNNING)
        if self.post_plan_workspace_tasks:
            task_stage = [task_stage for task_stage in self.task_stages if task_stage.stage is WorkspaceTaskStage.POST_PLAN][0]

            # Iterate over task results and execute
            for task_result in task_stage.task_results:
                task_result.execute()

        self.queue_worker_job()

    def handle_post_plan_running(self):
        """Handle post-plan running, checking for status of tasks"""
        task_stages = [task_stage for task_stage in self.task_stages if task_stage.stage is WorkspaceTaskStage.POST_PLAN]

        completed = True
        should_continue = True
        if len(task_stages) == 0:
            # No task stages - no tasks available
            pass
        elif len(task_stages) == 1:
            task_stage = task_stages[0]
            should_continue, completed = task_stage.check_status()

        if should_continue:
            if completed:
                self.update_status(RunStatus.POST_PLAN_COMPLETED)
            self.queue_worker_job()

    def handle_post_plan_completed(self):
        """Handle post plan completed, waiting for run to be confirmed"""
        # Check if plan was confirmed before entering the state
        if self.auto_apply or self.confirmed:
            self.update_status(RunStatus.CONFIRMED)
            self.queue_worker_job()

    def handle_confirmed(self):
        """Handle confirmed state"""
        # Handle pre-apply tasks.
        if self.pre_apply_workspace_tasks:
            task_stage = [task_stage for task_stage in self.task_stages if task_stage.stage is WorkspaceTaskStage.PRE_APPLY][0]

            # Iterate over task results and execute
            for task_result in task_stage.task_results:
                task_result.execute()


        self.update_status(RunStatus.PRE_APPLY_RUNNING)
        self.queue_worker_job()

    def handle_pre_apply_running(self):
        """Handle pre-apply running, waiting for task stages to execute"""
        task_stages = [task_stage for task_stage in self.task_stages if task_stage.stage is WorkspaceTaskStage.PRE_APPLY]

        completed = True
        should_continue = True
        if len(task_stages) == 0:
            # No task stages - no tasks available
            pass
        elif len(task_stages) == 1:
            task_stage = task_stages[0]
            should_continue, completed = task_stage.check_status()

        if should_continue:
            if completed:
                self.update_status(RunStatus.PRE_APPLY_COMPLETED)
                self.update_status(RunStatus.APPLY_QUEUED)
                self.queue_agent_job(job_type=JobQueueType.APPLY)
            else:
                self.queue_worker_job()

    def handle_apply_queued(self):
        """Handle apply_queued state"""
        session = Database.get_session()
        self.update_status(RunStatus.APPLYING)
        self.plan.apply.execute()
        session.refresh(self)
        if self.status == RunStatus.CANCELED:
            return
        elif self.plan.apply.status is terrarun.terraform_command.TerraformCommandState.ERRORED:
            self.update_status(RunStatus.ERRORED)
            return
        else:
            self.update_status(RunStatus.APPLIED)

    def execute_next_step(self):
        """Execute terraform command"""
        # Handle plan job
        print("Run Status: " + str(self.status))

        if self.status is RunStatus.PLAN_QUEUED:
            self.execute_plan()

        # Handle apply job
        elif self.status is RunStatus.APPLY_QUEUED:
            self.handle_apply_queued()

    def generate_state_version(self, work_dir):
        """Generate state version from state file."""
        state_content = None
        with open(os.path.join(work_dir, 'terraform.tfstate'), 'r') as state_file_fh:
            state_content = state_file_fh.readlines()
        state_json = json.loads('\n'.join(state_content))
        state_version = terrarun.models.state_version.StateVersion.create_from_state_json(run=self, state_json=state_json)

        return state_version

    def update_status(self, new_status, current_user=None, session=None):
        """Update state of run."""
        if self.status is RunStatus.CANCELED:
            print(f"Ignoring run status update to {str(new_status)} as status is CANCELLED")

        print(f"Updating job status to from {str(self.status)} to {str(new_status)}")
        should_commit = False
        if session is None:
            session = Database.get_session()
            session.refresh(self)
            should_commit = True

        audit_event = AuditEvent(
            organisation=self.configuration_version.workspace.organisation,
            user_id=current_user.id if current_user else None,
            object_id=self.id,
            object_type=self.ID_PREFIX,
            old_value=Database.encode_value(self.status.value) if self.status else None,
            new_value=Database.encode_value(new_status.value),
            event_type=AuditEventType.STATUS_CHANGE)

        self.status = new_status

        session.add(self)
        session.add(audit_event)
        if should_commit:
            session.commit()

    def queue_plan(self):
        """Queue for plan"""
        self.update_status(RunStatus.QUEUING)
        self.update_status(RunStatus.PLAN_QUEUED)

        # Requeue to be applied
        self.queue_agent_job(job_type=JobQueueType.PLAN)

    def confirm(self, comment, user):
        """Queue apply job"""
        # Mark job as confirmed
        self.update_attributes(confirmed=True)
        # If the job has already eached POST_PLAN_COMPLETED,
        # meaning that there is no longer queued, trigger
        # a worker job
        if self.status is RunStatus.POST_PLAN_COMPLETED:
            self.queue_worker_job()

        # @TODO Do something with comment

    def queue_agent_job(self, job_type):
        """Queue a run to be executed."""
        self._queue_job(agent_type=JobQueueAgentType.AGENT, job_type=job_type)

    def queue_worker_job(self):
        """Queue a run to be executed."""
        self._queue_job(agent_type=JobQueueAgentType.WORKER, job_type=None)

    def _queue_job(self, agent_type, job_type):
        """Queue a run to be executed"""
        session = Database.get_session()
        run_queue = RunQueue(run_id=self.id, agent_type=agent_type, job_type=job_type)
        session.add(run_queue)
        session.commit()

    @property
    def plan(self):
        """Get latest plan"""
        if self.plans:
            return self.plans[-1]
        return None

    def get_api_details(self, api_request: ApiRequest=None):
        """Return API details."""
        # Get status change audit events
        session = Database.get_session()
        audit_events = {
            '{}-at'.format(Database.decode_blob(event.new_value).replace('_', '-')): terrarun.utils.datetime_to_json(event.timestamp)
            for event in session.query(AuditEvent).where(
                AuditEvent.object_id==self.id,
                AuditEvent.object_type==self.ID_PREFIX,
                AuditEvent.event_type==AuditEventType.STATUS_CHANGE)
        }

        # @TODO Remove check for api_request object once all APIs use this methodology
        if api_request and api_request.has_include(ApiRequest.Includes.CONFIGURATION_VERSION) and self.configuration_version:
            api_request.add_included(self.configuration_version.get_api_details(api_request))

        return {
            "id": self.api_id,
            "type": "runs",
            "attributes": {
                "actions": {
                    "is-cancelable": True,
                    "is-confirmable": True,
                    "is-discardable": False,
                    "is-force-cancelable": False
                },
                "canceled-at": None,
                "created-at": terrarun.utils.datetime_to_json(self.created_at),
                "has-changes": self.plan.has_changes if self.plan else False,
                "auto-apply": self.auto_apply,
                "allow-empty-apply": False,
                "is-destroy": self.is_destroy,
                "message": self.message,
                "plan-only": self.plan_only,
                "source": "tfe-api",
                "status-timestamps": audit_events,
                "status": self.status.value,
                "trigger-reason": "manual",
                "target-addrs": self.target_addrs,
                "permissions": {
                    "can-apply": True,
                    "can-cancel": True,
                    "can-comment": True,
                    "can-discard": True,
                    "can-force-execute": True,
                    "can-force-cancel": True,
                    "can-override-policy-check": True
                },
                "refresh": self.refresh,
                "refresh-only": self.refresh_only,
                "replace-addrs": self.replace_addrs,
                "variables": []
            },
            "relationships": {
                "apply": {'data': {'id': self.plan.apply.api_id, 'type': 'applies'}} if self.plan is not None and self.plan.apply is not None else {},
                "comments": {},
                "configuration-version": {
                    'data': {'id': self.configuration_version.api_id, 'type': 'configuration-versions'}
                },
                "cost-estimate": {},
                "created-by": {
                    "data": {
                        "id": self.created_by.api_id,
                        "type": "users"
                    },
                    "links": {
                        "related": f"/api/v2/runs/{self.api_id}/created-by"
                    }
                } if self.created_by else {},
                "input-state-version": {},
                "plan": {'data': {'id': self.plan.api_id, 'type': 'plans'}} if self.plan is not None else {},
                "run-events": {},
                "policy-checks": {},
                "workspace": {'data': {'id': self.configuration_version.workspace.api_id, 'type': 'workspaces'}},
                "workspace-run-alerts": {},
                "task-stages": {
                    "data": [
                        task_stage.get_relationship()
                        for task_stage in self.task_stages
                    ]
                }
            },
            "links": {
                "self": f"/api/v2/runs/{self.api_id}"
            }
        }
