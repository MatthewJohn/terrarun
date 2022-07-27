

import json
import subprocess

from terrarun.terraform_command import TerraformCommand, TerraformCommandState


class Apply(TerraformCommand):

    ID_PREFIX = 'apply'

    def execute(self):
        """Execute apply"""
        self._pull_latest_state()

        self._status = TerraformCommandState.RUNNING
        action = 'apply'

        self._output += b"""
================================================
Command has started

Executed remotely on terrarun server
================================================
"""

        plan_out_file = 'TFRUN_PLAN_OUT'
        terraform_version = self._run._attributes.get('terraform_version') or '1.1.7'
        terraform_binary = f'terraform-{terraform_version}'
        command = [terraform_binary, action, '-input=false', '-auto-approve', plan_out_file]

        init_rc = self._run_command([terraform_binary, 'init', '-input=false'])
        if init_rc:
            self._status = TerraformCommandState.ERRORED
            return

        apply_rc = self._run_command(command)

        self.generate_state_version()

        if apply_rc:
            self._status = TerraformCommandState.ERRORED
        else:
            self._status = TerraformCommandState.FINISHED

    @property
    def state_version_relationships(self):
        """List of state version relationships"""
        relationships = []
        if self._state_version:
            relationships.append({
                "id": self._state_version._id,
                "type": "state-versions"
            })
        if self._run._plan._state_version:
            relationships.append({
                "id": self._run._plan._state_version._id,
                "type": "state-versions"
            })

        return relationships


    def get_api_details(self):
        """Return API details for plan"""
        return {
            "id": self._id,
            "type": "applies",
            "attributes": {
                "execution-details": {
                    # "agent-id": "agent-S1Y7tcKxXPJDQAvq",
                    # "agent-name": "agent_01",
                    # "agent-pool-id": "apool-Zigq2VGreKq7nwph",
                    # "agent-pool-name": "first-pool",
                    # "mode": "agent",
                },
                "status": "finished",
                "status-timestamps": {
                    "queued-at": "2018-10-17T18:58:27+00:00",
                    "started-at": "2018-10-17T18:58:29+00:00",
                    "finished-at": "2018-10-17T18:58:37+00:00"
                },
                "log-read-url": f"https://local-dev.dock.studio/api/v2/applies/{self._id}/log",
                "resource-additions": 0,
                "resource-changes": 0,
                "resource-destructions": 0
            },
            "relationships": {
                "state-versions": {
                    "data": self.state_version_relationships
                }
            },
            "links": {
                "self": f"/api/v2/applies/{self._id}"
            }
        }