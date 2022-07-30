

import json
import subprocess

import sqlalchemy
import sqlalchemy.orm

from terrarun.database import Base, Database
from terrarun.terraform_command import TerraformCommand, TerraformCommandState


class Plan(TerraformCommand, Base):

    ID_PREFIX = 'plan'

    __tablename__ = 'plan'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    run_id = sqlalchemy.Column(sqlalchemy.ForeignKey("run.id"), nullable=False)
    run = sqlalchemy.orm.relationship("Run", back_populates="plans")

    state_version_id = sqlalchemy.Column(sqlalchemy.ForeignKey("state_version.id"), nullable=True)
    state_version = sqlalchemy.orm.relationship("StateVersion", back_populates="plan", uselist=False)

    applies = sqlalchemy.orm.relation("Apply", back_populates="plan")

    status = sqlalchemy.Column(sqlalchemy.Enum(TerraformCommandState))

    plan_output_id = sqlalchemy.Column(sqlalchemy.ForeignKey("blob.id"), nullable=True)
    plan_output = sqlalchemy.orm.relation("Blob", foreign_keys=[plan_output_id])
    log_id = sqlalchemy.Column(sqlalchemy.ForeignKey("blob.id"), nullable=True)
    log = sqlalchemy.orm.relation("Blob", foreign_keys=[log_id])

    @classmethod
    def create(cls, run):
        """Create plan and return instance."""
        plan = cls(run=run, status=TerraformCommandState.PENDING)
        session = Database.get_session()
        session.add(plan)
        session.commit()
        return plan

    def execute(self):
        """Execute plan"""
        work_dir = self.configuration_version.extract_configuration()
        self._pull_latest_state(work_dir)

        self._status = TerraformCommandState.RUNNING
        action = None
        if  self._run._attributes.get('refresh_only'):
            action = 'refresh'
        else:
            action = 'plan'

        self._append_output(b"""================================================
Command has started

Executed remotely on terrarun server
================================================
""")

        plan_out_file = 'TFRUN_PLAN_OUT'
        terraform_version = self.run.terraform_version or '1.1.7'
        terraform_binary = f'terraform-{terraform_version}'
        command = [terraform_binary, action, '-input=false', f'-out={plan_out_file}']

        init_rc = self._run_command([terraform_binary, 'init', '-input=false'])
        if init_rc:
            self.update_status(TerraformCommandState.ERRORED)
            return

        if self.run.refresh:
            refresh_rc = self._run_command([terraform_binary, 'refresh', '-input=false'])
            if refresh_rc:
                self.update_status(TerraformCommandState.ERRORED)
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
            self.update_status(TerraformCommandState.ERRORED)
        else:
            self.update_status(TerraformCommandState.FINISHED)

    def update_status(self, new_status):
        """Update state of plan."""
        session = Database.get_session()
        session.refresh(self)
        self.status = new_status
        session.add(self)
        session.commit()

    @property
    def has_changes(self):
        """Return is plan has changes"""
        if not self.plan_output.data:
            return False
        return bool(self.resource_additions or self.resource_destructions or self.resource_changes)

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