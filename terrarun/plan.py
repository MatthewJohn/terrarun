

from enum import Enum
import terrarun.run
import subprocess


class PlanState(Enum):

    PENDING = 'pending'
    MANAGE_QUEUED = 'managed_queued'
    QUEUED = 'queued'
    RUNNING = 'running'
    ERRORED = 'errored'
    CANCELED = 'canceled'
    FINISHED = 'finished'
    UNREACHABLE = 'unreachable'


class Plan:

    PLANS = {}

    @classmethod
    def get_by_id(cls, id_):
        """Obtain plan instance by ID."""
        if id_ in cls.PLANS:
            return cls.PLANS[id_]
        return None

    @classmethod
    def create(cls, run, **attributes):
        """Create plan and return instance."""
        id_ = 'plan-ntv3HbhJqvFzam{id}'.format(id=str(len(cls.PLANS)).zfill(2))
        run = cls(run=run, id_=id_, **attributes)
        cls.PLANS[id_] = run

        return run

    def __init__(self, run, id_):
        """Create run"""
        self._id = id_
        self._run = run
        self._output = b""

    def execute(self):
        """Execute plan"""
        self._status = PlanState.PENDING
        action = None
        if  self._run._attributes.get('refresh_only'):
            action = 'refresh'
        else:
            action = 'plan'

        terraform_version = self._run._attributes.get('terraform_version') or '1.1.7'
        command = [f'terraform-{terraform_version}', action]

        self._status = PlanState.RUNNING

        print('InIT STARTING!!!')
        init_proc = subprocess.Popen(
            [f'terraform-{terraform_version}', 'init'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=self._run._configuration_version._extract_dir)

        for line in iter(init_proc.stdout.readline, ""):
            self._output += line

        init_rc = init_proc.communicate()
        print('INIT FINISHED!!!')
        if init_rc:
            print('INITN FAILED!!!')
            self._status = PlanState.ERRORED
            return

        print('PLAN STARTING!!!')
        plan_proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=self._run._configuration_version._extract_dir)

        for line in iter(plan_proc.stdout.readline, ""):
            self._output += line

        plan_rc = plan_proc.communicate()
        if plan_rc:
            self._status = PlanState.ERRORED
        else:
            self._status = PlanState.FINISHED

        print('PLAN COMPLETE!!!')


    def get_api_details(self):
        """Return API details for plan"""
        return {
            "id": self._id,
            "type": "plans",
            "attributes": {
                "execution-details": {
                    "mode": "remote",
                },
                "has-changes": True,
                "resource-additions": 0,
                "resource-changes": 1,
                "resource-destructions": 0,
                "status": "finished",
                "status-timestamps": {
                    "queued-at": "2018-07-02T22:29:53+00:00",
                    "pending-at": "2018-07-02T22:29:53+00:00",
                    "started-at": "2018-07-02T22:29:54+00:00",
                    "finished-at": "2018-07-02T22:29:58+00:00"
                },
                "log-read-url": f"https://local-dev.dock.studio/api/v2/plans/{self._id}/log"
            },
            "relationships": {
                "state-versions": {}
            },
            "links": {
                "self": f"/api/v2/plans/{self._id}",
                "json-output": f"/api/v2/plans/{self._id}/json-output"
            }
        }