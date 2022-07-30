
from enum import Enum
import json
import os
import queue

import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.sql

from terrarun.database import Base, Database
import terrarun.plan
import terrarun.apply
import terrarun.state_version
from terrarun.run_queue import RunQueue
import terrarun.terraform_command
from terrarun.base_object import BaseObject


class RunStatus(Enum):

    PENDING = 'pending'
    FETCHING = 'fetching'
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
    def create(cls, configuration_version, **attributes):
        """Create run and return instance."""
        session = Database.get_session()
        run = Run(
            configuration_version=configuration_version,
            status=RunStatus.PENDING,
            **attributes)
        session.add(run)
        session.commit()
        plan = terrarun.plan.Plan.create(run=run)
        terrarun.apply.Apply.create(plan=plan)

        # Queue plan job
        run.queue_plan()
        return run

    def execute_next_step(self):
        """Execute terraform command"""
        # Handle plan job
        print("Job Status: " + str(self.status))
        if self.status is RunStatus.PLAN_QUEUED:
            self.update_status(RunStatus.PLANNING)
            self.plan.execute()
            if self.plan.status is terrarun.terraform_command.TerraformCommandState.ERRORED:
                self.update_status(RunStatus.ERRORED)
                return
            else:
                self.update_status(RunStatus.PLANNED)

            if self.plan_only or self.configuration_version.speculative:
                self.update_status(RunStatus.PLANNED_AND_FINISHED)
                return

            if self.auto_apply:
                self.queue_apply()

        # Handle apply job
        elif self.status is RunStatus.APPLY_QUEUED:
            self.update_status(RunStatus.APPLYING)
            self.plan.apply.execute()
            if self.plan.apply.status is terrarun.terraform_command.TerraformCommandState.ERRORED:
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

    def update_status(self, new_status):
        """Update state of run."""
        print(f"Updating job status to from {str(self.status)} to {str(new_status)}")
        session = Database.get_session()
        session.refresh(self)
        self.status = new_status
        session.add(self)
        session.commit()

    def queue_plan(self):
        """Queue for plan"""
        self.update_status(RunStatus.PLAN_QUEUED)

        # Requeue to be applied
        self.add_to_queue_table()

    def queue_apply(self, comment=None):
        """Queue apply job"""
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
                "created-at": "2021-05-24T07:38:04.171Z",
                "has-changes": self.plan.has_changes if self.plan else False,
                "auto-apply": self.auto_apply,
                "allow-empty-apply": False,
                "is-destroy": self.is_destroy,
                "message": self.message,
                "plan-only": self.plan_only,
                "source": "tfe-api",
                "status-timestamps": {
                    "plan-queueable-at": "2021-05-24T07:38:04+00:00"
                },
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
                "created-by": {},
                "input-state-version": {},
                "plan": {'data': {'id': self.plan.api_id, 'type': 'plans'}} if self.plan is not None else {},
                "run-events": {},
                "policy-checks": {},
                "workspace": {'data': {'id': self.configuration_version.workspace.api_id, 'type': 'workspaces'}},
                "workspace-run-alerts": {}
            },
            "links": {
                "self": f"/api/v2/runs/{self.api_id}"
            }
        }