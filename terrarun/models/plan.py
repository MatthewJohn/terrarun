# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

import json
import os
import subprocess
from typing import Optional

import sqlalchemy
import sqlalchemy.orm

import terrarun.config
import terrarun.models.audit_event
import terrarun.utils
import terrarun.models.apply
import terrarun.models.agent
from terrarun.database import Base, Database
from terrarun.logger import get_logger
from terrarun.models.blob import Blob
import terrarun.workspace_execution_mode
from terrarun.terraform_command import TerraformCommand, TerraformCommandState

logger = get_logger(__name__)


class Plan(TerraformCommand, Base):

    ID_PREFIX = 'plan'

    __tablename__ = 'plan'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    api_id_fk = sqlalchemy.Column(sqlalchemy.ForeignKey("api_id.id"), nullable=True)
    api_id_obj = sqlalchemy.orm.relationship("ApiId", foreign_keys=[api_id_fk])

    run_id = sqlalchemy.Column(sqlalchemy.ForeignKey("run.id"), nullable=False)
    run = sqlalchemy.orm.relationship("Run", back_populates="plans")

    state_version_id = sqlalchemy.Column(sqlalchemy.ForeignKey("state_version.id"), nullable=True)
    state_version = sqlalchemy.orm.relationship("StateVersion", back_populates="plan", uselist=False)

    applies = sqlalchemy.orm.relationship("Apply", back_populates="plan")

    status = sqlalchemy.Column(sqlalchemy.Enum(TerraformCommandState))

    plan_output_id = sqlalchemy.Column(sqlalchemy.ForeignKey("blob.id"), nullable=True)
    _plan_output = sqlalchemy.orm.relationship("Blob", foreign_keys=[plan_output_id])
    plan_output_binary_id = sqlalchemy.Column(sqlalchemy.ForeignKey("blob.id"), nullable=True)
    _plan_output_binary = sqlalchemy.orm.relationship("Blob", foreign_keys=[plan_output_binary_id])
    providers_schemas_id = sqlalchemy.Column(sqlalchemy.ForeignKey("blob.id"), nullable=True)
    _providers_schemas = sqlalchemy.orm.relationship("Blob", foreign_keys=[providers_schemas_id])
    log_id = sqlalchemy.Column(sqlalchemy.ForeignKey("blob.id"), nullable=True)
    log = sqlalchemy.orm.relationship("Blob", foreign_keys=[log_id])

    agent_id: int = sqlalchemy.Column(sqlalchemy.ForeignKey("agent.id", name="fk_apply_agent_id"), nullable=True)
    agent: Optional['terrarun.models.agent.Agent'] = sqlalchemy.orm.relationship("Agent", back_populates="plans")
    execution_mode: Optional['terrarun.workspace_execution_mode.WorkspaceExecutionMode'] = sqlalchemy.Column(
        sqlalchemy.Enum(terrarun.workspace_execution_mode.WorkspaceExecutionMode),
        nullable=True, default=None)

    ## Attributes provided by terraform agent
    _has_changes = sqlalchemy.Column(sqlalchemy.Boolean, default=None, nullable=True, name="has_changes")
    _resource_additions = sqlalchemy.Column(sqlalchemy.Integer, default=None, nullable=True, name="resource_additions")
    _resource_changes = sqlalchemy.Column(sqlalchemy.Integer, default=None, nullable=True, name="resource_changes")
    _resource_destructions = sqlalchemy.Column(sqlalchemy.Integer, default=None, nullable=True, name="resource_destructions")

    @classmethod
    def create(cls, run):
        """Create plan and return instance."""
        plan = cls(run=run)
        session = Database.get_session()
        session.add(plan)
        session.commit()

        # Generate API ID, so that it can't be performed silently on multiple
        # duplicate requests, causing the API ID to be generated twice and
        # different values returned in different responses
        plan.api_id
        plan.update_status(TerraformCommandState.PENDING)
        return plan

    @property
    def apply(self) -> Optional['terrarun.models.apply.Apply']:
        """Get latest apply"""
        if self.applies:
            return self.applies[-1]
        return None

    def assign_to_agent(self, agent: 'terrarun.models.agent.Agent', execution_mode: 'terrarun.workspace_execution_mode.WorkspaceExecutionMode'):
        """Assign plan to agent and set current execution mode"""
        self.agent = agent
        self.execution_mode = execution_mode
        session = Database.get_session()
        session.add(self)
        session.commit()

    @property
    def plan_output(self):
        """Return plan output value"""
        if self._plan_output and self._plan_output.data:
            return json.loads(self._plan_output.data.decode('utf-8'))
        return {}

    @plan_output.setter
    def plan_output(self, value):
        """Set plan output"""
        session = Database.get_session()

        if self._plan_output:
            plan_output_blob = self._plan_output
            session.refresh(plan_output_blob)
        else:
            plan_output_blob = Blob()

        plan_output_blob.data = bytes(json.dumps(value), 'utf-8')

        session.add(plan_output_blob)
        session.refresh(self)
        self._plan_output = plan_output_blob
        session.add(self)
        session.commit()

    @property
    def providers_schemas(self):
        """Return plan output value"""
        if self._providers_schemas and self._providers_schemas.data:
            return json.loads(self._providers_schemas.data.decode('utf-8'))
        return {}

    @providers_schemas.setter
    def providers_schemas(self, value):
        """Set plan output"""
        session = Database.get_session()

        if self._providers_schemas:
            providers_schemas_blob = self._providers_schemas
            session.refresh(providers_schemas_blob)
        else:
            providers_schemas_blob = Blob()

        providers_schemas_blob.data = bytes(json.dumps(value), 'utf-8')

        session.add(providers_schemas_blob)
        session.refresh(self)
        self._providers_schemas = providers_schemas_blob
        session.add(self)
        session.commit()

    @property
    def plan_output_binary(self):
        """Return plan output value"""
        if self._plan_output_binary and self._plan_output_binary.data:
            return self._plan_output_binary.data
        return {}

    @plan_output_binary.setter
    def plan_output_binary(self, value):
        """Set plan output"""
        session = Database.get_session()

        if self._plan_output_binary:
            plan_output_binary_blob = self._plan_output_binary
            session.refresh(plan_output_binary_blob)
        else:
            plan_output_binary_blob = Blob()

        plan_output_binary_blob.data = value

        session.add(plan_output_binary_blob)
        session.refresh(self)
        self._plan_output_binary = plan_output_binary_blob
        session.add(self)
        session.commit()

    @property
    def has_changes(self):
        """Return is plan has changes"""
        # If set on row, return value
        if self._has_changes is not None:
            return self._has_changes

        # Deprecated functionality based on agent not provided
        # details
        if not self.plan_output:
            return False
        return bool(self.resource_additions or self.resource_destructions or self.resource_changes)

    @has_changes.setter
    def has_changes(self, new_value):
        """Update has_changes DB value"""
        self._has_changes = new_value

    @property
    def resource_additions(self):
        """Return number of resources to be added"""
        # If set on row, return value
        if self._resource_additions is not None:
            return self._resource_additions

        # Deprecated functionality based on agent not provided
        # details
        count = 0
        for resource in self.plan_output.get('resource_changes', {}):
            if 'create' in resource.get('change', {}).get('actions', []):
                count += 1
        return count

    @resource_additions.setter
    def resource_additions(self, new_value):
        """Update resource_additions DB value"""
        self._resource_additions = new_value

    @property
    def resource_destructions(self):
        """Return number of resources to be destroyed"""
        # If set on row, return value
        if self._resource_additions is not None:
            return self._resource_additions

        # Deprecated functionality based on agent not provided
        # details
        count = 0
        for resource in self.plan_output.get('resource_changes', {}):
            if 'delete' in resource.get('change', {}).get('actions', []):
                count += 1
        return count

    @resource_destructions.setter
    def resource_destructions(self, new_value):
        """Update resource_destructions DB value"""
        self._resource_destructions = new_value

    @property
    def resource_changes(self):
        """Return number of resources to be changed"""
        # If set on row, return value
        if self._resource_changes is not None:
            return self._resource_changes

        # Deprecated functionality based on agent not provided
        # details
        count = 0
        for resource in self.plan_output.get('resource_changes', {}):
            if 'update' in resource.get('change', {}).get('actions', []):
                count += 1
        return count

    @resource_changes.setter
    def resource_changes(self, new_value):
        """Update resource_changes DB value"""
        self._resource_changes = new_value
