

from enum import Enum
import json
import os
from time import sleep
import terrarun.run
import subprocess

from terrarun.state_version import StateVersion


class PlanState(Enum):

    PENDING = 'pending'
    MANAGE_QUEUED = 'managed_queued'
    QUEUED = 'queued'
    RUNNING = 'running'
    ERRORED = 'errored'
    CANCELED = 'canceled'
    FINISHED = 'finished'
    UNREACHABLE = 'unreachable'


class TerraformCommand:

    ID_PREFIX = 'nope'

    INSTANCES = {}

    @classmethod
    def get_by_id(cls, id_):
        """Obtain plan instance by ID."""
        if id_ in cls.INSTANCES:
            return cls.INSTANCES[id_]
        return None

    @classmethod
    def create(cls, run):
        """Create plan and return instance."""
        id_ = '{id_prefix}-ntv3HbhJqvFzam{id}'.format(
            id_prefix=cls.ID_PREFIX,
            id=str(len(cls.INSTANCES)).zfill(2))
        run = cls(run=run, id_=id_)
        cls.INSTANCES[id_] = run

        return run

    def __init__(self, run, id_):
        """Create run"""
        self._id = id_
        self._run = run
        self._output = b""
        self._state_version = None
        self._status = PlanState.PENDING

    def execute(self):
        raise NotImplementedError

    def _run_command(self, command):
        command_proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=self._run._configuration_version._extract_dir)

        # Obtain all stdout
        while True:
            line = command_proc.stdout.readline()
            if line:
                self._output += line
            elif command_proc.poll() is not None:
                break

        return command_proc.returncode

    def generate_state_version(self):
        """Generate state version from state file."""
        state_content = None
        with open(os.path.join(self._run._configuration_version._extract_dir, 'terraform.tfstate'), 'r') as state_file_fh:
            state_content = state_file_fh.readlines()
        state_json = json.loads('\n'.join(state_content))
        self._state_version = StateVersion.create_from_state_json(run=self._run, state_json=state_json)

        # Register state with workspace
        self._run._workspace._latest_state = self._state_version

class Plan(TerraformCommand):

    ID_PREFIX = 'plan'

    def execute(self):
        """Execute plan"""
        self._status = PlanState.RUNNING
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

        init_rc = self._run_command([f'terraform-{terraform_version}', 'init', '-input=false'])
        if init_rc:
            self._status = PlanState.ERRORED
            return

        if self._run._attributes.get('refresh', True):
            refresh_rc = self._run_command([f'terraform-{terraform_version}', 'refresh', '-input=false'])
            if refresh_rc:
                self._status = PlanState.ERRORED
                return

            # Extract state
            self.generate_state_version()

        plan_rc = self._run_command(command)
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
                "status": self._status.value,
                "status-timestamps": {
                    "queued-at": "2018-07-02T22:29:53+00:00",
                    "pending-at": "2018-07-02T22:29:53+00:00",
                    "started-at": "2018-07-02T22:29:54+00:00",
                    "finished-at": "2018-07-02T22:29:58+00:00"
                },
                "log-read-url": f"https://local-dev.dock.studio/api/v2/plans/{self._id}/log"
            },
            "relationships": {
                "state-versions": {'data': {'id': self._state_version._id, 'type': 'state-versions'}} if self._state_version else {}
            },
            "links": {
                "self": f"/api/v2/plans/{self._id}",
                "json-output": f"/api/v2/plans/{self._id}/json-output"
            }
        }