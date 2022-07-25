
from enum import Enum


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

        return run

    def __init__(self, configuration_version, id_, **attributes):
        """Store member variables"""
        self._id = id_
        self._configuration_version = configuration_version
        self._attributes = attributes
        self._status = RunStatus.PENDING

    def get_api_details(self):
        """Return API details."""
        return {
            "data": {
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
                    "auto-apply": False,
                    "allow-empty-apply": False,
                    "is-destroy": False,
                    "message": "Custom message",
                    "plan-only": False,
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
                    "refresh": False,
                    "refresh-only": False,
                    "replace-addrs": None,
                    "variables": []
                },
                "relationships": {
                    "apply": {},
                    "comments": {},
                    "configuration-version": {},
                    "cost-estimate": {},
                    "created-by": {},
                    "input-state-version": {},
                    "plan": {},
                    "run-events": {},
                    "policy-checks": {},
                    "workspace": {},
                    "workspace-run-alerts": {}
                },
                "links": {
                    "self": "/api/v2/runs/run-CZcmD7eagjhyX0vN"
                }
            }
        }
