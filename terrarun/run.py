
import subprocess
from enum import Enum
import queue
from time import sleep

import terrarun.plan


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


class Run:

    RUNS = {}
    RUNS_BY_WORKSPACE = {}
    WORKER_QUEUE = queue.Queue()

    @classmethod
    def get_by_id(cls, id_):
        """Obtain run instance by ID."""
        if id_ in cls.RUNS:
            return cls.RUNS[id_]
        return None

    @classmethod
    def create(cls, configuration_version, **attributes):
        """Create run and return instance."""
        id_ = 'run-ntv3HbhJqvFzam{id}'.format(id=str(len(cls.RUNS)).zfill(2))
        run = cls(configuration_version=configuration_version, id_=id_, **attributes)
        cls.RUNS[id_] = run
        if configuration_version._workspace._id not in cls.RUNS_BY_WORKSPACE:
            cls.RUNS_BY_WORKSPACE[configuration_version._workspace._id] = []
        cls.RUNS_BY_WORKSPACE[configuration_version._workspace._id].append(run)

        return run

    @classmethod
    def get_runs_by_workspace(cls, workspace):
        """Return all runs for a given workspace"""
        return cls.RUNS_BY_WORKSPACE.get(workspace._id, [])

    def __init__(self, configuration_version, id_, **attributes):
        """Store member variables"""
        self._id = id_
        self._plan = None
        self._configuration_version = configuration_version
        self._attributes = {
            'auto_apply': False,
            'message': '',
            'plan_only': False,
            'refresh': True,
            'refresh_only': False
        }
        self._attributes.update(attributes)
        self._status = RunStatus.PENDING

        self._plan = terrarun.plan.Plan.create(self)
        self._status = RunStatus.PLAN_QUEUED
        self.__class__.WORKER_QUEUE.put(self.execute_next_step)
        self._plan._status = terrarun.plan.PlanState.PENDING

    def execute_next_step(self):
        """Execute terraform command"""
        if self._status is RunStatus.PLAN_QUEUED:
            self._status = RunStatus.PLANNING
            self._plan.execute()
            if self._plan._status is terrarun.plan.PlanState.ERRORED:
                self._status = RunStatus.ERRORED
            else:
                self._status = RunStatus.PLANNED

            if self._attributes.get('plan_only') or self._configuration_version.speculative:
                self._status = RunStatus.PLANNED_AND_FINISHED

    def get_api_details(self):
        """Return API details."""
        return {
            "id": self._id,
            "type": "runs",
            "attributes": {
                "actions": {
                    "is-cancelable": True,
                    "is-confirmable": False,
                    "is-discardable": False,
                    "is-force-cancelable": False
                },
                "canceled-at": None,
                "created-at": "2021-05-24T07:38:04.171Z",
                "has-changes": False,
                "auto-apply": self._attributes.get('auto_apply'),
                "allow-empty-apply": False,
                "is-destroy": False,
                "message": self._attributes.get('message'),
                "plan-only": self._attributes.get('plan_only', False),
                "source": "tfe-api",
                "status-timestamps": {
                    "plan-queueable-at": "2021-05-24T07:38:04+00:00"
                },
                "status": self._status.value,
                "trigger-reason": "manual",
                "target-addrs": None,
                "permissions": {
                    "can-apply": True,
                    "can-cancel": True,
                    "can-comment": True,
                    "can-discard": True,
                    "can-force-execute": True,
                    "can-force-cancel": True,
                    "can-override-policy-check": True
                },
                "refresh": self._attributes.get('refresh', False),
                "refresh-only": self._attributes.get('refresh_only', False),
                "replace-addrs": None,
                "variables": []
            },
            "relationships": {
                "apply": {},
                "comments": {},
                "configuration-version": {
                    'data': {'id': self._configuration_version._id, 'type': 'configuration-versions'}
                },
                "cost-estimate": {},
                "created-by": {},
                "input-state-version": {},
                "plan": {'data': {'id': self._plan._id, 'type': 'plans'}} if self._plan is not None else {},
                "run-events": {},
                "policy-checks": {},
                "workspace": {'data': {'id': self._configuration_version._workspace._id, 'type': 'workspaces'}},
                "workspace-run-alerts": {}
            },
            "links": {
                "self": f"/api/v2/runs/{self._id}"
            }
        }