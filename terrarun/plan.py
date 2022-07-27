

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
        self._plan_output = {}

    def execute(self):
        raise NotImplementedError

    def _run_command(self, command):
        command_proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=self._run._configuration_version._extract_dir)

        # Obtain all stdout
        print_lines = True
        while True:
            line = command_proc.stdout.readline()
            if line:
                # Stop printing lines once line about
                # saving plan to output file is displayed and
                # display line about how to apply changes
                if line.startswith(b'Saved the plan to: '):
                    self._output += b'To perform exactly these actions, run the following command to apply:\n    terraform apply\n'
                    print_lines = False

                if print_lines:
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
        self._run._configuration_version._workspace._latest_state = self._state_version

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

        plan_out_file = 'TFRUN_PLAN_OUT'
        terraform_version = self._run._attributes.get('terraform_version') or '1.1.7'
        terraform_binary = f'terraform-{terraform_version}'
        command = [terraform_binary, action, '-input=false', f'-out={plan_out_file}']

        init_rc = self._run_command([terraform_binary, 'init', '-input=false'])
        if init_rc:
            self._status = PlanState.ERRORED
            return

        if self._run._attributes.get('refresh', True):
            refresh_rc = self._run_command([terraform_binary, 'refresh', '-input=false'])
            if refresh_rc:
                self._status = PlanState.ERRORED
                return

            # Extract state
            self.generate_state_version()

        plan_rc = self._run_command(command)

        plan_out_raw = subprocess.check_output(
            [terraform_binary, 'show', '-json', plan_out_file],
            cwd=self._run._configuration_version._extract_dir
        )
        self._plan_output = json.loads(plan_out_raw)

        if plan_rc:
            self._status = PlanState.ERRORED
        else:
            self._status = PlanState.FINISHED

    @property
    def has_changes(self):
        """Return is plan has changes"""
        if not self._plan_output:
            return False
        return bool(self._plan_output['resource_changes'])

    @property
    def resource_additions(self):
        count = 0
        for resource in self._plan_output.get('resource_changes', {}):
            if 'create' in resource.get('change', {}).get('actions', []):
                count += 1
        return count

    @property
    def resource_destructions(self):
        count = 0
        for resource in self._plan_output.get('resource_changes', {}):
            if 'delete' in resource.get('change', {}).get('actions', []):
                count += 1
        return count

    @property
    def resource_changes(self):
        count = 0
        for resource in self._plan_output.get('resource_changes', {}):
            if 'update' in resource.get('change', {}).get('actions', []):
                count += 1
        return count

    def get_api_details(self):
        """Return API details for plan"""
        return {
            "id": self._id,
            "type": "plans",
            "attributes": {
                "execution-details": {
                    "mode": "remote",
                },
                "has-changes": self.has_changes,
                "resource-additions": self.resource_additions,
                "resource-changes": self.resource_changes,
                "resource-destructions": self.resource_destructions,
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