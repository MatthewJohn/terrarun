
from enum import Enum
import json
import os
import subprocess

from terrarun.state_version import StateVersion


class TerraformCommandState(Enum):

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
    STATE_FILE = 'terraform.tfstate'

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
        self._status = TerraformCommandState.PENDING
        self._plan_output = {}

    def _pull_latest_state(self):
        """Pull latest version of state to working copy."""
        # No latest state available for workspace
        state_version = self._run._configuration_version._workspace._latest_state
        if not state_version or not state_version._state_json:
            return

        with open(os.path.join(self._run._configuration_version._extract_dir, self.STATE_FILE), 'w') as state_fh:
            state_fh.write(json.dumps(state_version._state_json))

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