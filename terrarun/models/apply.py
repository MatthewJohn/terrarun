# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

import os
import sqlalchemy
import sqlalchemy.orm
from typing import Optional

import terrarun.config
import terrarun.database
import terrarun.workspace_execution_mode
import terrarun.models.agent
import terrarun.models.plan
from terrarun.database import Base, Database
from terrarun.terraform_command import TerraformCommand, TerraformCommandState


class Apply(TerraformCommand, Base):

    ID_PREFIX = 'apply'

    __tablename__ = 'apply'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    api_id_fk = sqlalchemy.Column(sqlalchemy.ForeignKey("api_id.id"), nullable=True)
    api_id_obj = sqlalchemy.orm.relationship("ApiId", foreign_keys=[api_id_fk])

    plan_id: int = sqlalchemy.Column(sqlalchemy.ForeignKey("plan.id"), nullable=False)
    plan: 'terrarun.models.plan.Plan' = sqlalchemy.orm.relationship("Plan", back_populates="applies")

    state_version_id = sqlalchemy.Column(sqlalchemy.ForeignKey("state_version.id"), nullable=True)
    state_version = sqlalchemy.orm.relationship("StateVersion", back_populates="apply", uselist=False)

    log_id = sqlalchemy.Column(sqlalchemy.ForeignKey("blob.id"), nullable=True)
    log = sqlalchemy.orm.relationship("Blob", foreign_keys=[log_id])

    status = sqlalchemy.Column(sqlalchemy.Enum(TerraformCommandState))
    changes = sqlalchemy.Column(terrarun.database.Database.GeneralString)

    agent_id: int = sqlalchemy.Column(sqlalchemy.ForeignKey("agent.id", name="fk_apply_agent_id"), nullable=True)
    agent: Optional['terrarun.models.agent.Agent'] = sqlalchemy.orm.relationship("Agent", back_populates="applies")
    execution_mode: Optional['terrarun.workspace_execution_mode.WorkspaceExecutionMode'] = sqlalchemy.Column(
        sqlalchemy.Enum(terrarun.workspace_execution_mode.WorkspaceExecutionMode),
        nullable=True, default=None)

    @classmethod
    def create(cls, plan):
        """Create plan and return instance."""
        apply = cls(plan=plan)
        session = Database.get_session()
        session.add(apply)
        session.commit()
        # Generate API ID, so that it can't be performed silently on multiple
        # duplicate requests, causing the API ID to be generated twice and
        # different values returned in different responses
        apply.api_id
        apply.update_status(TerraformCommandState.PENDING)
        return apply

    def assign_to_agent(self, agent: 'terrarun.models.agent.Agent', execution_mode: 'terrarun.workspace_execution_mode.WorkspaceExecutionMode'):
        """Assign plan to agent and set current execution mode"""
        self.agent = agent
        self.execution_mode = execution_mode
        session = Database.get_session()
        session.add(self)
        session.commit()

    def _pull_plan_output(self, work_dir):
        """Create plan output file"""
        with open(os.path.join(work_dir, self.PLAN_OUTPUT_FILE), 'wb') as plan_fh:
            plan_fh.write(self.plan.plan_output_binary)

    @property
    def run(self):
        """Get run object"""
        return self.plan.run
