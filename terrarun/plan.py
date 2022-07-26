

from enum import Enum
from time import sleep
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
    def create(cls, run):
        """Create plan and return instance."""
        id_ = 'plan-ntv3HbhJqvFzam{id}'.format(id=str(len(cls.PLANS)).zfill(2))
        run = cls(run=run, id_=id_)
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

        self._output += b"""================================================
Command has started

Executed remotely on terrarun server
================================================
"""

        terraform_version = self._run._attributes.get('terraform_version') or '1.1.7'
        command = [f'terraform-{terraform_version}', action, '-input=false']

        self._status = PlanState.RUNNING

        init_proc = subprocess.Popen(
            [f'terraform-{terraform_version}', 'init', '-input=false'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=self._run._configuration_version._extract_dir)

        # Obtain all stdout
        while True:
            line = init_proc.stdout.readline()
            if line:
                self._output += line
            elif init_proc.poll() is not None:
                break

        # Wait for process to exit
        while init_proc.poll() is None:
            sleep(0.05)

        init_rc = init_proc.returncode
        if init_rc:
            self._status = PlanState.ERRORED
            return

        if self._run._attributes('refresh', True):
            refresh_proc = subprocess.Popen(
                [f'terraform-{terraform_version}', 'refresh', '-input=false'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=self._run._configuration_version._extract_dir)

            # Obtain all stdout
            while True:
                line = refresh_proc.stdout.readline()
                if line:
                    self._output += line
                elif refresh_proc.poll() is not None:
                    break

            # Wait for process to exit
            while refresh_proc.poll() is None:
                sleep(0.05)

            refresh_rc = refresh_proc.returncode
            if refresh_rc:
                self._status = PlanState.ERRORED
                return

        plan_proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=self._run._configuration_version._extract_dir)

        for line in iter(plan_proc.stdout.readline, ""):
            self._output += line

        # Wait for process to exit
        while plan_proc.poll() is None:
            sleep(0.05)

        plan_rc = plan_proc.returncode
        if plan_rc:
            self._status = PlanState.ERRORED
        else:
            self._status = PlanState.FINISHED

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