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
from terrarun.audit_event import AuditEvent, AuditEventType

from terrarun.database import Base, Database
import terrarun.plan
import terrarun.apply
import terrarun.state_version
from terrarun.run_queue import RunQueue
from terrarun.task_result import TaskResultStatus
from terrarun.task_stage import TaskStage, TaskStageStatus
import terrarun.terraform_command
from terrarun.base_object import BaseObject
import terrarun.utils
import terrarun.config
from terrarun.workspace_task import WorkspaceTaskEnforcementLevel, WorkspaceTaskStage


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

    configuration_version_id = sqlalchemy.Column(sqlalchemy.ForeignKey("configuration_version.id"), nullable=False)
    configuration_version = sqlalchemy.orm.relationship("ConfigurationVersion", back_populates="runs")

    state_versions = sqlalchemy.orm.relation("StateVersion", back_populates="run")
    plans = sqlalchemy.orm.relation("Plan", back_populates="run")

    run_queue = sqlalchemy.orm.relation("RunQueue", back_populates="run", uselist=False)

    status = sqlalchemy.Column(sqlalchemy.Enum(RunStatus))
    auto_apply = sqlalchemy.Column(sqlalchemy.Boolean)
    message = sqlalchemy.Column(sqlalchemy.String)
    plan_only = sqlalchemy.Column(sqlalchemy.Boolean)
    refresh = sqlalchemy.Column(sqlalchemy.Boolean)
    refresh_only = sqlalchemy.Column(sqlalchemy.Boolean)
    is_destroy = sqlalchemy.Column(sqlalchemy.Boolean)
    _replace_addrs = sqlalchemy.Column("replace_addrs", sqlalchemy.String)
    _target_addrs = sqlalchemy.Column("target_addrs", sqlalchemy.String)
    _variables = sqlalchemy.Column("variables", sqlalchemy.String)
    terraform_version = sqlalchemy.Column(sqlalchemy.String)
    allow_empty_apply = sqlalchemy.Column(sqlalchemy.Boolean)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=sqlalchemy.sql.func.now())

    created_by_id = sqlalchemy.Column(sqlalchemy.ForeignKey("user.id", name="run_created_by_id_user_id"))
    created_by = sqlalchemy.orm.relation("User", foreign_keys=[created_by_id])

    task_stages = sqlalchemy.orm.relationship("TaskStage", back_populates="run")

    @property
    def replace_addrs(self):
        return json.loads(self._replace_addrs)

    @replace_addrs.setter
    def replace_addrs(self, value):
        self._replace_addrs = json.dumps(value)

    @property
    def target_addrs(self):
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
    def create(cls, configuration_version, created_by, **attributes):
        """Create run and return instance."""
        session = Database.get_session()
        run = Run(
            configuration_version=configuration_version,
            created_by=created_by,
            **attributes)
        session.add(run)
        session.commit()
        session.refresh(run)
        run.update_status(RunStatus.PENDING, current_user=created_by)
        # Queue to be processed
        run.add_to_queue_table()
        return run

    def cancel(self, user):
        """Cancel run"""
        self.update_status(RunStatus.CANCELED, current_user=user)

    @property
    def pre_plan_workspace_tasks(self):
        """Return list of workspace tasks for pre-plan"""
        return [
            workspace_task
            for workspace_task in self.configuration_version.workspace.workspace_tasks
            if workspace_task.stage == WorkspaceTaskStage.PRE_PLAN and workspace_task.active
        ]

    def execute_next_step(self):
        """Execute terraform command"""
        session = Database.get_session()
        config = terrarun.config.Config()
        # Handle plan job
        print("Job Status: " + str(self.status))

        if self.status is RunStatus.PENDING:

            # Create plan, as the terraform client expects this
            # to immediately exist
            terrarun.plan.Plan.create(run=self)

            # Handle pre-run tasks.
            if self.pre_plan_workspace_tasks:
                task_stage = TaskStage.create(
                    run=self,
                    stage=WorkspaceTaskStage.PRE_PLAN,
                    workspace_tasks=self.pre_plan_workspace_tasks)
                self.update_status(RunStatus.PRE_PLAN_RUNNING)

                # Iterate over task results and execute
                for task_result in task_stage.task_results:
                    task_result.execute()

            self.update_status(RunStatus.PRE_PLAN_RUNNING)
            # Queue plan
            self.add_to_queue_table()

        # Check status of pre-plan tasks
        elif self.status is RunStatus.PRE_PLAN_RUNNING:
            task_stages = [task_stage for task_stage in self.task_stages if task_stage.stage is WorkspaceTaskStage.PRE_PLAN]

            still_running = 0

            # No task stages - no tasks available
            if len(task_stages) == 0:
                pass
            elif len(task_stages) == 1:
                task_stage = task_stages[0]
                # Iterate through each task stage result
                for task_result in task_stage.task_results:
                    is_mandatory = task_result.workspace_task.enforcement_level is WorkspaceTaskEnforcementLevel.MANDATORY

                    # If task result was cancelled and the
                    # check is mandatory, move to complete
                    if task_result.status is TaskResultStatus.CANCELED and is_mandatory:
                        self.update_status(RunStatus.CANCELED)
                        return

                    # Check if any mandatory tasks have errored
                    elif (task_result.status in [
                            TaskResultStatus.FAILED,
                            TaskResultStatus.ERRRORED,
                            TaskResultStatus.UNREACHABLE] and
                            is_mandatory):
                        self.update_status(RunStatus.ERRORED)
                        return

                    # If task is still running, check if time has elapsed
                    elif task_result.status in [TaskResultStatus.PENDING, TaskResultStatus.RUNNING]:
                        if task_result.start_time and (task_result.start_time + datetime.timedelta(minutes=10)) < datetime.datetime.now():
                            # Update task result status to errored
                            task_result.update_status(TaskResultStatus.ERRRORED)
                            # If task is mandatory, treat run as errored
                            if is_mandatory:
                                self.update_status(RunStatus.ERRORED)
                                return
                        still_running += 1
                    
                    else:
                        print('Unknown task result status: ', task_result.status)

            # If no tasks are still running, update
            # state to completed
            if not still_running:
                self.update_status(RunStatus.PRE_PLAN_COMPLETED)
                self.add_to_queue_table()

        elif self.status is RunStatus.PRE_PLAN_COMPLETED:
            self.queue_plan()

        elif self.status is RunStatus.PLAN_QUEUED:
            self.update_status(RunStatus.PLANNING)
            plan = self.plan
            self.plan.execute()
            session.refresh(self)
            if self.status == RunStatus.CANCELED:
                return
            elif plan.status is terrarun.terraform_command.TerraformCommandState.ERRORED:
                self.update_status(RunStatus.ERRORED)
                return
            else:
                self.update_status(RunStatus.PLANNED)

            if self.plan_only or self.configuration_version.speculative or not self.plan.has_changes:
                self.update_status(RunStatus.PLANNED_AND_FINISHED)
                return

            if self.auto_apply:
                terrarun.apply.Apply.create(plan=self.plan)
                self.queue_apply()

        # Handle apply job
        elif self.status is RunStatus.APPLY_QUEUED:
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

    def generate_state_version(self, work_dir):
        """Generate state version from state file."""
        state_content = None
        with open(os.path.join(work_dir, 'terraform.tfstate'), 'r') as state_file_fh:
            state_content = state_file_fh.readlines()
        state_json = json.loads('\n'.join(state_content))
        state_version = terrarun.state_version.StateVersion.create_from_state_json(run=self, state_json=state_json)

        return state_version

    def update_status(self, new_status, current_user=None, session=None):
        """Update state of run."""
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
        self.add_to_queue_table()

    def queue_apply(self, comment, user):
        """Queue apply job"""
        self.update_status(RunStatus.CONFIRMED, current_user=user)
        self.update_status(RunStatus.APPLY_QUEUED)

        # Requeue to be applied
        self.add_to_queue_table()

        # @TODO Do something with comment

    def add_to_queue_table(self):
        """Queue a run to be executed."""
        session = Database.get_session()
        run_queue = RunQueue(run=self)
        session.add(run_queue)
        session.commit()

    @property
    def plan(self):
        """Get latest plan"""
        if self.plans:
            return self.plans[-1]
        return None

    def get_api_details(self):
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
                    "data": [task_stage.get_relationship() for task_stage in self.task_stages]
                }
            },
            "links": {
                "self": f"/api/v2/runs/{self.api_id}"
            }
        }
