# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

import json
import os
from enum import Enum
from typing import Optional, List

import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.sql

import terrarun.config
import terrarun.database
import terrarun.models.apply
import terrarun.models.plan
import terrarun.models.state_version
import terrarun.models.run_flow
import terrarun.models.team_workspace_access
import terrarun.permissions
import terrarun.permissions.workspace
import terrarun.terraform_command
import terrarun.models.tool
import terrarun.utils
import terrarun.models.configuration
import terrarun.models.user
import terrarun.models.task_stage
import terrarun.auth_context
from terrarun.models.workspace_task import WorkspaceTaskEnforcementLevel, WorkspaceTaskStage
from terrarun.api_request import ApiRequest
from terrarun.database import Base, Database
from terrarun.errors import (
    CustomTerraformVersionCannotBeUsedError,
    FailedToUnlockWorkspaceError,
    RunCannotBeCancelledError,
    RunCannotBeDiscardedError,
    TerraformVersionNotSetError,
)
from terrarun.logger import get_logger
import terrarun.models.audit_event
from terrarun.models.base_object import BaseObject
from terrarun.models.run_queue import JobQueueAgentType, JobQueueType, RunQueue
from terrarun.models.task_stage import TaskStage
from terrarun.models.workspace_task import (
    WorkspaceTaskStage,
)

logger = get_logger(__name__)


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
    api_id_obj = sqlalchemy.orm.relationship("ApiId", foreign_keys=[api_id_fk])

    configuration_version_id: int = sqlalchemy.Column(sqlalchemy.ForeignKey("configuration_version.id"), nullable=False)
    configuration_version: 'terrarun.models.configuration.ConfigurationVersion' = sqlalchemy.orm.relationship("ConfigurationVersion", back_populates="runs")

    state_versions: List['terrarun.models.state_version.StateVersion'] = sqlalchemy.orm.relationship("StateVersion", back_populates="run")
    plans = sqlalchemy.orm.relationship("Plan", back_populates="run")

    run_queue = sqlalchemy.orm.relationship("RunQueue", back_populates="run", uselist=False)

    status = sqlalchemy.Column(sqlalchemy.Enum(terrarun.models.run_flow.RunStatus))
    confirmed = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    confirmed_by_id = sqlalchemy.Column(sqlalchemy.ForeignKey("user.id", name="run_confirmed_by_id_user_id"), nullable=True)
    confirmed_by = sqlalchemy.orm.relationship("User", foreign_keys=[confirmed_by_id])
    auto_apply = sqlalchemy.Column(sqlalchemy.Boolean)
    message = sqlalchemy.Column(terrarun.database.Database.GeneralString)
    plan_only = sqlalchemy.Column(sqlalchemy.Boolean)
    refresh = sqlalchemy.Column(sqlalchemy.Boolean)
    refresh_only = sqlalchemy.Column(sqlalchemy.Boolean)
    is_destroy = sqlalchemy.Column(sqlalchemy.Boolean)
    _replace_addrs = sqlalchemy.Column("replace_addrs", terrarun.database.Database.GeneralString)
    _target_addrs = sqlalchemy.Column("target_addrs", terrarun.database.Database.GeneralString)
    _variables = sqlalchemy.Column("variables", terrarun.database.Database.GeneralString)
    tool_id: Optional[int] = sqlalchemy.Column(sqlalchemy.ForeignKey("tool.id"), nullable=True)
    tool: Optional['terrarun.models.tool.Tool'] = sqlalchemy.orm.relationship("Tool")
    allow_empty_apply = sqlalchemy.Column(sqlalchemy.Boolean)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=sqlalchemy.sql.func.now())

    created_by_id = sqlalchemy.Column(sqlalchemy.ForeignKey("user.id", name="run_created_by_id_user_id"), nullable=True)
    created_by = sqlalchemy.orm.relationship("User", foreign_keys=[created_by_id])

    task_stages: List['terrarun.models.task_stage.TaskStage'] = sqlalchemy.orm.relationship("TaskStage", back_populates="run")

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
            raise TerraformVersionNotSetError(
                'Terraform version not configured',
                'The Terraform version must be configured in project/workspace'
            )

        if ((tool := attributes.get('tool')) and
                tool != configuration_version.workspace.tool and
                not attributes.get('plan_only')):
            raise CustomTerraformVersionCannotBeUsedError(
                'Custom Terraform version cannot be used for non-refresh-only runs',
                'The version of Terraform requested does not match the project and cannot be used in applies'
            )

        # If configuration version is speculative, the run must
        # be plan only
        if configuration_version.speculative:
            attributes['plan_only'] = True

        # Check rules for environment to ensure that environment can create a run
        can_create_run = configuration_version.can_create_run(attributes.get("plan_only", False))
        if can_create_run is not True:
            raise can_create_run

        run = Run(
            configuration_version=configuration_version,
            created_by=created_by,
            message=message,
            **attributes)
        session.add(run)

        session.commit()
        session.refresh(run)

        # Generate API ID, so that it can't be performed silently on multiple
        # duplicate requests, causing the API ID to be generated twice and
        # different values returned in different responses
        run.api_id
        run.update_status(terrarun.models.run_flow.RunStatus.PENDING, current_user=created_by)

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

        # Queue to be processed
        run.queue_worker_job()
        return run

    def cancel(self, user):
        """Cancel run"""
        if self.status in [terrarun.models.run_flow.RunStatus.APPLIED, terrarun.models.run_flow.RunStatus.PLANNED_AND_FINISHED, terrarun.models.run_flow.RunStatus.POST_PLAN_COMPLETED]:
            raise RunCannotBeCancelledError("Run is not in a state that can be cancelled")
        self.update_status(terrarun.models.run_flow.RunStatus.CANCELED, current_user=user)

    def discard(self, user):
        """Discard run"""
        if self.status is not terrarun.models.run_flow.RunStatus.POST_PLAN_COMPLETED:
            raise RunCannotBeDiscardedError("Run is not in a state that can be discarded")
        if not self.configuration_version.workspace.unlock(run=self):
            raise FailedToUnlockWorkspaceError("Failed to unlock run")
        self.update_status(terrarun.models.run_flow.RunStatus.DISCARDED)

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

    @property
    def run_events(self):
        """Return run events"""
        # @TODO See https://gitlab.dockstudios.co.uk/pub/terra/terrarun/-/issues/123
        return []

    def handling_pending(self):
        """Create plan and setup pre-plan tasks"""
        # Attempt to lock workspace
        if not self.configuration_version.workspace.lock(run=self, reason="Locked for run"):
            # If locking failed, just requeue worker job
            self.queue_worker_job()
            return

        # Create plan, as the terraform client expects this
        # to immediately exist
        terrarun.models.plan.Plan.create(run=self)
        self.update_status(terrarun.models.run_flow.RunStatus.PRE_PLAN_RUNNING)

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
                self.update_status(terrarun.models.run_flow.RunStatus.PRE_PLAN_COMPLETED)
            self.queue_worker_job()

    def handle_planned(self):
        """Handle planned state"""
        # If successfully planned, move to pre-plan tasks
        self.update_status(terrarun.models.run_flow.RunStatus.POST_PLAN_RUNNING)
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
                self.update_status(terrarun.models.run_flow.RunStatus.POST_PLAN_COMPLETED)
            self.queue_worker_job()

    def handle_post_plan_completed(self):
        """Handle post plan completed, waiting for run to be confirmed"""
        # Check if plan was confirmed before entering the state
        if self.auto_apply or self.confirmed:
            self.update_status(
                terrarun.models.run_flow.RunStatus.CONFIRMED,
                current_user=self.confirmed_by
            )
            self.queue_worker_job()

    def handle_confirmed(self):
        """Handle confirmed state"""
        # Handle pre-apply tasks.
        if self.pre_apply_workspace_tasks:
            task_stage = [task_stage for task_stage in self.task_stages if task_stage.stage is WorkspaceTaskStage.PRE_APPLY][0]

            # Iterate over task results and execute
            for task_result in task_stage.task_results:
                task_result.execute()


        self.update_status(terrarun.models.run_flow.RunStatus.PRE_APPLY_RUNNING)
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
                self.update_status(terrarun.models.run_flow.RunStatus.PRE_APPLY_COMPLETED)
                self.update_status(terrarun.models.run_flow.RunStatus.APPLY_QUEUED)
                self.queue_agent_job(job_type=JobQueueType.APPLY)
            else:
                self.queue_worker_job()

    def update_status(self, new_status, current_user=None, session=None):
        """Update state of run."""
        if self.status is terrarun.models.run_flow.RunStatus.CANCELED:
            logger.warning("Ignoring run status update to %s as status is CANCELLED", new_status)

        logger.info("Updating job status to from %s to %s", self.status, new_status)
        should_commit = False
        if session is None:
            session = Database.get_session()
            session.refresh(self)
            should_commit = True

        audit_event = terrarun.models.audit_event.AuditEvent(
            organisation=self.configuration_version.workspace.organisation,
            user_id=current_user.id if current_user else None,
            object_id=self.id,
            object_type=self.ID_PREFIX,
            old_value=Database.encode_value(self.status.value) if self.status else None,
            new_value=Database.encode_value(new_status.value),
            event_type=terrarun.models.audit_event.AuditEventType.STATUS_CHANGE)

        self.status = new_status

        session.add(self)
        session.add(audit_event)
        if should_commit:
            session.commit()

    def unlock_workspace(self):
        """Unlock workspace after run completes/errors"""
        if not self.configuration_version.workspace.unlock(run=self):
            raise Exception("Failed to unlock workspace")

    def queue_plan(self):
        """Queue for plan"""
        self.update_status(terrarun.models.run_flow.RunStatus.QUEUING)
        self.update_status(terrarun.models.run_flow.RunStatus.PLAN_QUEUED)

        # Requeue to be applied
        self.queue_agent_job(job_type=JobQueueType.PLAN)

    def confirm(self, comment: Optional[str], user: Optional['terrarun.models.user.User']):
        """Queue apply job"""
        # @TODO Add comment to change
        # Mark job as confirmed
        self.update_attributes(confirmed=True, confirmed_by=user)
        # If the job has already eached POST_PLAN_COMPLETED,
        # meaning that there is no longer queued, trigger
        # a worker job
        if self.status is terrarun.models.run_flow.RunStatus.POST_PLAN_COMPLETED:
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
    def plan(self) -> Optional['terrarun.models.plan.Plan']:
        """Get latest plan"""
        if self.plans:
            return self.plans[-1]
        return None

    @property
    def flow(self) -> Optional['terrarun.models.run_flow.BaseRunFlow']:
        """Obtain run flow for current status"""
        return terrarun.models.run_flow.RunFlowFactory.get_flow_by_status(self.status)

    def get_api_details(self, auth_context: 'terrarun.auth_context.AuthContext', api_request: ApiRequest | None = None):
        """Return API details."""
        # Get status change audit events
        session = Database.get_session()
        audit_events_types = {
            "pending-at": terrarun.models.run_flow.RunStatus.PENDING,
            "applied-at": terrarun.models.run_flow.RunStatus.APPLIED,
            "planned-at": terrarun.models.run_flow.RunStatus.PLANNED,
            "queuing-at": terrarun.models.run_flow.RunStatus.QUEUING,
            "applying-at": terrarun.models.run_flow.RunStatus.APPLYING,
            "planning-at": terrarun.models.run_flow.RunStatus.PLANNING,
            "confirmed-at": terrarun.models.run_flow.RunStatus.CONFIRMED,
            "plan-queued-at": terrarun.models.run_flow.RunStatus.PLAN_QUEUED,
            "apply-queued-at": terrarun.models.run_flow.RunStatus.APPLY_QUEUED,
            "queuing-apply-at": terrarun.models.run_flow.RunStatus.APPLY_QUEUED,
            "cost-estimated-at": terrarun.models.run_flow.RunStatus.COST_ESTIMATED,
            "plan-queueable-at": terrarun.models.run_flow.RunStatus.PLAN_QUEUED,
            "cost-estimating-at": terrarun.models.run_flow.RunStatus.COST_ESTIMATING
        }
        all_audit_events = {
            terrarun.models.run_flow.RunStatus(Database.decode_blob(event.new_value)): terrarun.utils.datetime_to_json(event.timestamp)
            for event in session.query(terrarun.models.audit_event.AuditEvent).where(
                terrarun.models.audit_event.AuditEvent.object_id==self.id,
                terrarun.models.audit_event.AuditEvent.object_type==self.ID_PREFIX,
                terrarun.models.audit_event.AuditEvent.event_type==terrarun.models.audit_event.AuditEventType.STATUS_CHANGE)
        }
        audit_events = {
            label: all_audit_events[enum_val]
            for label, enum_val in audit_events_types.items()
            if enum_val in all_audit_events
        }

        # @TODO Remove check for api_request object once all APIs use this methodology
        if api_request and api_request.has_include(ApiRequest.Includes.CONFIGURATION_VERSION) and self.configuration_version:
            api_request.add_included(self.configuration_version.get_api_details(api_request=api_request, auth_context=auth_context))

        permissions = {
            "can-apply": False,
            "can-cancel": False,
            "can-comment": False,
            "can-discard": False,
            "can-force-execute": False,
            "can-force-cancel": False,
            "can-override-policy-check": False
        }
        if auth_context.user:
            workspace_permissions = terrarun.permissions.workspace.WorkspacePermissions(
                current_user=auth_context.user,
                workspace=self.configuration_version.workspace
            )
            permissions["can-apply"] = workspace_permissions.check_access_type(
                runs=terrarun.models.team_workspace_access.TeamWorkspaceRunsPermission.APPLY
            )
            permissions["can-cancel"] = workspace_permissions.check_access_type(
                runs=(
                    terrarun.models.team_workspace_access.TeamWorkspaceRunsPermission.PLAN
                    if self.plan_only else
                    terrarun.models.team_workspace_access.TeamWorkspaceRunsPermission.APPLY
                )
            )
            permissions["can-comment"] = workspace_permissions.check_access_type(
                runs=(
                    terrarun.models.team_workspace_access.TeamWorkspaceRunsPermission.PLAN
                )
            )
            permissions["can-discard"] = workspace_permissions.check_access_type(
                runs=(
                    terrarun.models.team_workspace_access.TeamWorkspaceRunsPermission.PLAN
                    if self.plan_only else
                    terrarun.models.team_workspace_access.TeamWorkspaceRunsPermission.APPLY
                )
            )
            permissions["can-force-execute"] = workspace_permissions.check_permission(
                permission=terrarun.models.team_workspace_access.TeamWorkspaceAccessType.ADMIN
            )
            permissions["can-force-cancel"] = workspace_permissions.check_permission(
                permission=terrarun.models.team_workspace_access.TeamWorkspaceAccessType.ADMIN
            )
            permissions["can-override-policy-check"] = workspace_permissions.check_permission(
                permission=terrarun.models.team_workspace_access.TeamWorkspaceAccessType.ADMIN
            )

        actions = None
        if flow := self.flow:
            actions = flow.get_run_actions()

        return {
            "id": self.api_id,
            "type": "runs",
            "attributes": {
                "actions": actions,
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
                "permissions": permissions,
                "refresh": self.refresh,
                "refresh-only": self.refresh_only,
                "replace-addrs": self.replace_addrs,
                "variables": self.variables,
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
