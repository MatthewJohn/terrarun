# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from typing import Optional
import json

import sqlalchemy
import sqlalchemy.orm

from terrarun.models.base_object import BaseObject
from terrarun.database import Base, Database
import terrarun.database
from terrarun.models.blob import Blob
from terrarun.models.state_version_output import StateVersionOutput
import terrarun.models.user

from terrarun.utils import datetime_to_json


class StateVersion(Base, BaseObject):

    ID_PREFIX = 'sv'

    __tablename__ = 'state_version'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    api_id_fk = sqlalchemy.Column(sqlalchemy.ForeignKey("api_id.id"), nullable=True)
    api_id_obj = sqlalchemy.orm.relation("ApiId", foreign_keys=[api_id_fk])

    workspace_id = sqlalchemy.Column(sqlalchemy.ForeignKey("workspace.id"), nullable=False)
    workspace = sqlalchemy.orm.relationship("Workspace", back_populates="state_versions")

    run_id = sqlalchemy.Column(sqlalchemy.ForeignKey("run.id"), nullable=True)
    run = sqlalchemy.orm.relationship("Run", back_populates="state_versions")

    # Optional references to either plan that generated state or apply
    apply = sqlalchemy.orm.relation("Apply", back_populates="state_version")
    plan = sqlalchemy.orm.relation("Plan", back_populates="state_version")

    resources_processed = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    state_version_outputs = sqlalchemy.orm.relation("StateVersionOutput", back_populates="state_version")

    state_json_id = sqlalchemy.Column(sqlalchemy.ForeignKey("blob.id"), nullable=True)
    _state_json = sqlalchemy.orm.relation("Blob", foreign_keys=[state_json_id])

    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=sqlalchemy.sql.func.now())

    created_by_id: Optional[int] = sqlalchemy.Column(sqlalchemy.ForeignKey("user.id"), nullable=True)
    created_by: 'terrarun.models.user.User' = sqlalchemy.orm.relationship("User")

    @property
    def state_json(self):
        """Return plan output value"""
        if self._state_json and self._state_json.data:
            return json.loads(self._state_json.data.decode('utf-8'))
        return {}

    @state_json.setter
    def state_json(self, value):
        """Set plan output"""
        session = Database.get_session()

        if self._state_json:
            state_json_blob = self._state_json
            session.refresh(state_json_blob)
        else:
            state_json_blob = Blob()

        state_json_blob.data = bytes(json.dumps(value), 'utf-8')

        session.add(state_json_blob)
        # @TODO this does not work when creating object
        #session.refresh(self)
        self._state_json = state_json_blob
        session.add(self)
        session.commit()

    @classmethod
    def create_from_state_json(cls, run, workspace, state_json, session=None):
        """Create StateVersion from state_json."""
        sv = cls(run=run, workspace=workspace, created_by=run.created_by)
        session = Database.get_session()
        session.add(sv)
        session.commit()
        sv.state_json=state_json

        return sv

    @classmethod
    def get_state_version_to_process(cls):
        """Obtain first unprocessed state version"""
        session = Database.get_session()
        return session.query(cls).where(cls.resources_processed!=True).first()

    @property
    def resources(self):
        """Return resources"""
        return self.state_json['resources']

    @property
    def providers(self):
        """Return modules"""
        providers = {}
        for res in self.resources:
            if res['provider'] not in providers:
                providers[res['provider']] = 0
            providers[res['provider']] += 1
        return providers

    @property
    def modules(self):
        """Return modules"""
        modules = {}
        for res in self.resources:
            module = res['module'] if 'module' in res else 'root'
            if module not in modules:
                modules[module] = {}
            resource_type = res['type'] if res['mode'] == 'managed' else '{mode}.{type}'.format(mode=res['mode'], type=res['type'])

            if resource_type not in modules[module]:
                modules[module][resource_type] = 0
            
            modules[module][resource_type] += 1

        return modules

    @property
    def serial(self):
        """Return serial of state"""
        return self.state_json['serial']

    @property
    def version(self):
        """Return serial of state"""
        return self.state_json['version']

    @property
    def terraform_version(self):
        return self.state_json['terraform_version']

    def process_resources(self):
        """Process resources"""
        # Create state version outputs for each output
        # in state
        for output_name, output_data in self.state_json.get("outputs").items():
            StateVersionOutput.create_from_state_output(state_version=self, name=output_name, data=output_data)

        # Set resources_processed to True
        self.update_attributes(resources_processed=True)

    def get_api_details(self):
        """Return API details."""
        return {
            "id": self.api_id,
            "type": "state-versions",
            "attributes": {
                "created-at": datetime_to_json(self.created_at),
                "size": 940,
                "hosted-state-download-url": f"/api/v2/state-versions/{self.api_id}/download",
                "modules": self.modules,
                "providers": self.providers,
                "resources": self.resources,
                "resources-processed": bool(self.resources_processed),
                "serial": self.serial,
                "state-version": self.version,
                "terraform-version": self.terraform_version,
                "vcs-commit-url": "https://gitlab.com/my-organization/terraform-test/-/commit/abcdef12345",
                "vcs-commit-sha": "abcdef12345"
            },
            "relationships": {
                "run": {
                    "data": {
                        "id": self.run.api_id,
                        "type": "runs"
                    }
                } if self.run else {},
                "created-by": {
                    "data": {
                        "id": self.created_by.api_id,
                        "type": "users"
                    },
                    "links": {
                        "self": f"/api/v2/users/{self.created_by.api_id}",
                        "related": f"/api/v2/runs/{self.api_id}/created-by"
                    }
                } if self.created_by else {},
                "workspace": {
                    "data": {
                        "id": self.workspace.api_id,
                        "type": "workspaces"
                    }
                },
                "outputs": {
                    "data": [
                        state_version_output.get_relationship()
                        for state_version_output in self.state_version_outputs
                    ]
                }
            },
            "links": {
                "self": f"/api/v2/state-versions/{self.api_id}"
            }
        }
