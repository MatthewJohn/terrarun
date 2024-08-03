# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

from enum import Enum
from typing import Optional, Dict, Any
import json

import sqlalchemy
import sqlalchemy.orm

import terrarun.config
from terrarun.models.base_object import BaseObject
from terrarun.database import Base, Database
import terrarun.database
from terrarun.models.blob import Blob
from terrarun.models.state_version_output import StateVersionOutput
import terrarun.models.user
import terrarun.presign
import terrarun.utils
import terrarun.models.workspace
import terrarun.models.run
import terrarun.models.run_queue
import terrarun.auth_context


class StateVersionStatus(Enum):
    """Status of agent"""

    PENDING = "pending"
    FINALIZED = "finalized"
    DISCARDED = "discarded"
    BACKING_DATA_SOFT_DELETED = "backing_data_soft_deleted"
    BACKING_DATA_PERMANENTLY_DELETED = "backing_data_permanently_deleted"


class StateVersion(Base, BaseObject):

    ID_PREFIX = 'sv'

    __tablename__ = 'state_version'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    api_id_fk = sqlalchemy.Column(sqlalchemy.ForeignKey("api_id.id"), nullable=True)
    api_id_obj = sqlalchemy.orm.relationship("ApiId", foreign_keys=[api_id_fk])

    workspace_id: int = sqlalchemy.Column(sqlalchemy.ForeignKey("workspace.id"), nullable=False)
    workspace: 'terrarun.models.workspace.Workspace' = sqlalchemy.orm.relationship("Workspace", back_populates="state_versions")

    run_id: int = sqlalchemy.Column(sqlalchemy.ForeignKey("run.id"), nullable=True)
    run: Optional['terrarun.models.run.Run'] = sqlalchemy.orm.relationship("Run", back_populates="state_versions")

    # Optional references to either plan that generated state or apply
    apply = sqlalchemy.orm.relationship("Apply", back_populates="state_version")
    plan = sqlalchemy.orm.relationship("Plan", back_populates="state_version")

    # @TODO Populate old data and set to False, if null to avoid required conversion to bool and set nullable=False
    resources_processed = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    state_version_outputs = sqlalchemy.orm.relationship("StateVersionOutput", back_populates="state_version")

    state_id = sqlalchemy.Column(sqlalchemy.ForeignKey("blob.id", name="fk_blob_state_version_state"), nullable=True)
    _state = sqlalchemy.orm.relation("Blob", foreign_keys=[state_id])

    json_state_id = sqlalchemy.Column(sqlalchemy.ForeignKey("blob.id", name="fk_blob_state_version_json_state"), nullable=True)
    _json_state = sqlalchemy.orm.relationship("Blob", foreign_keys=[json_state_id])

    # Attributes provided by user to verify state
    lineage: Optional[str] = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=True, default=None)
    md5: Optional[str] = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=True, default=None)

    # Values cached from json data
    serial: Optional[int] = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=None)
    state_version: Optional[int] = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=None, unique=True)
    terraform_version: Optional[str] = sqlalchemy.Column(Database.GeneralString, nullable=True, default=None)

    intermediate: bool = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=True)

    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=sqlalchemy.sql.func.now())

    created_by_id: Optional[int] = sqlalchemy.Column(sqlalchemy.ForeignKey("user.id"), nullable=True)
    created_by: Optional['terrarun.models.user.User'] = sqlalchemy.orm.relationship("User")

    status: StateVersionStatus = sqlalchemy.Column(sqlalchemy.Enum(StateVersionStatus),
                                                   nullable=False,
                                                   default=StateVersionStatus.PENDING)

    @property
    def state(self) -> Optional[Dict[str, Any]]:
        """Return state JSON"""
        if self._state and self._state.data:
            return json.loads(self._state.data.decode('utf-8'))
        return None

    @state.setter
    def state(self, value: Optional[Dict[str, Any]]):
        """Set plan output"""
        session = Database.get_session()

        if self._state:
            state_blob = self._state
            session.refresh(state_blob)
        else:
            state_blob = Blob()

        if value is not None:
            state_blob.data = bytes(json.dumps(value), 'utf-8')
        else:
            state_blob.data = None

        session.add(state_blob)
        # @TODO this does not work when creating object
        #session.refresh(self)
        self._state = state_blob
        session.add(self)
        session.commit()

    @property
    def json_state(self) -> Optional[Dict[str, Any]]:
        """Return plan output value"""
        if self._json_state and self._json_state.data:
            return json.loads(self._json_state.data.decode('utf-8'))
        return None

    @json_state.setter
    def json_state(self, value: Optional[Dict[str, Any]]):
        """Set plan output"""
        session = Database.get_session()

        if self._json_state:
            json_state_blob = self._json_state
            session.refresh(json_state_blob)
        else:
            json_state_blob = Blob()

        if value is not None:
            json_state_blob.data = bytes(json.dumps(value), 'utf-8')
        else:
            json_state_blob.data = None

        session.add(json_state_blob)
        # @TODO this does not work when creating object
        #session.refresh(self)
        self._json_state = json_state_blob
        session.add(self)
        session.commit()

    @classmethod
    def create(cls, run, workspace, created_by, state, json_state, session=None):
        """Create StateVersion from state_json."""
        sv = cls(run=run, workspace=workspace, created_by=created_by)
        session = Database.get_session()
        session.add(sv)
        session.commit()
        if json_state:
            sv.json_state = json_state

        sv.status = StateVersionStatus.PENDING
        if state:
            sv.status = StateVersionStatus.FINALIZED
            sv.state = state

        sv.intermediate = True

        session.add(sv)
        session.commit()

        return sv

    @classmethod
    def get_state_version_to_process(cls):
        """Obtain first unprocessed state version"""
        session = Database.get_session()
        return session.query(cls).where(
            cls.resources_processed!=True,
            cls.status==StateVersionStatus.FINALIZED,
        ).first()

    def handle_state_upload(self, state: Any, auth_context: 'terrarun.auth_context.AuthContext') -> bool:
        """Handle upload of state"""
        if not self.can_upload_state(auth_context=auth_context) or self._state is not None:
            return False

        # Set status to FINALIZED
        self.update_attributes(status=StateVersionStatus.FINALIZED)

        self.state = state
        return True

    def handle_json_state_upload(self, json_state: Any, auth_context: 'terrarun.auth_context.AuthContext') -> bool:
        """Handle upload of state"""
        if not self.can_upload_state(auth_context=auth_context) or self._state is not None:
            return False

        self.json_state = json_state
        return True

    def can_upload_state(self, auth_context: 'terrarun.auth_context.AuthContext') -> bool:
        """Whether state can be uploaded"""
        if self.status is not StateVersionStatus.PENDING:
            return False

        if not self.workspace.locked:
            return False

        # @TODO Don't use IDs, but logic to check if both are none or both the IDs match is less obvious
        if self.workspace.locked_by_run:
            if self.workspace.locked_by_run.api_id != self.run.api_id:
                return False
        elif self.workspace.locked_by_user_id != auth_context.user.id if auth_context.user else None:
            return False

        return True

    def get_state_upload_url(self, auth_context: 'terrarun.auth_context.AuthContext'):
        """Generate state upload URL"""
        if self.can_upload_state(auth_context=auth_context) and self._state is None:
            url_generator = terrarun.presign.PresignedUrlGenerator()
            return url_generator.create_url(auth_context=auth_context, path=f"/api/v2/state-versions/{self.api_id}/upload")

    def get_json_state_upload_url(self, auth_context: 'terrarun.auth_context.AuthContext'):
        """Generate state upload URL"""
        if self.can_upload_state(auth_context=auth_context) and self._json_state is None:
            return None
        url_generator = terrarun.presign.PresignedUrlGenerator()
        return url_generator.create_url(auth_context=auth_context, path=f"/api/v2/state-versions/{self.api_id}/json-upload")

    def get_state_download_url(self, auth_context: 'terrarun.auth_context.AuthContext'):
        """Generate state upload URL"""
        if self._state is None:
            return None
        url_generator = terrarun.presign.PresignedUrlGenerator()
        return url_generator.create_url(auth_context=auth_context, path=f"/api/v2/state-versions/{self.api_id}/download")

    def get_json_state_download_url(self, auth_context: 'terrarun.auth_context.AuthContext'):
        """Generate state upload URL"""
        if self._json_state is None:
            return None
        url_generator = terrarun.presign.PresignedUrlGenerator()
        return url_generator.create_url(auth_context=auth_context, path=f"/api/v2/state-versions/{self.api_id}/json-download")

    @property
    def resources(self):
        """Return resources"""
        return self.state['resources'] if self.state else []

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

    def process_resources(self):
        """Process resources"""
        # Create state version outputs for each output
        # in state
        if state := self.state:
            for output_name, output_data in state.get("outputs").items():
                StateVersionOutput.create_from_state_output(state_version=self, name=output_name, data=output_data)

            self.update_attributes(
                state_version=state.get("version"),
                serial=state.get("serial"),
                lineage=state.get("lineage"),
                terraform_version=state.get("terraform_version"),
        )

        # Set resources_processed to True and mark as finalized
        self.update_attributes(
            resources_processed=True,
            status=StateVersionStatus.FINALIZED,
        )
