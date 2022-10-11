# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import sqlalchemy
import sqlalchemy.orm

from terrarun.base_object import BaseObject
from terrarun.database import Base
from terrarun.workspace import Workspace
from terrarun.workspace_execution_mode import WorkspaceExecutionMode


class MetaWorkspace(Base, BaseObject):

    ID_PREFIX = 'mws'
    MINIMUM_NAME_LENGTH = 3

    __tablename__ = 'meta_workspace'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)

    organisation_id = sqlalchemy.Column(sqlalchemy.ForeignKey(
        "organisation.id", name="fk_meta_workspace_organisation_id_organisation_id"),
        nullable=False)
    organisation = sqlalchemy.orm.relationship("Organisation", back_populates="meta_workspaces")

    workspaces = sqlalchemy.orm.relation("Workspace", back_populates="meta_workspace")

    lifecycle_id = sqlalchemy.Column(
        sqlalchemy.ForeignKey("lifecycle.id", name="fk_meta_workspace_lifecycle_id_lifecycle_id"),
        nullable=False)
    lifecycle = sqlalchemy.orm.relationship("Lifecycle", back_populates="meta_workspaces")

    allow_destroy_plan = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    auto_apply = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    execution_mode = sqlalchemy.Column(sqlalchemy.Enum(WorkspaceExecutionMode), nullable=True, default=WorkspaceExecutionMode.REMOTE)
    file_triggers_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=True, name="file_triggers_enabled")
    global_remote_state = sqlalchemy.Column(sqlalchemy.Boolean, default=False, name="global_remote_state")
    operations = sqlalchemy.Column(sqlalchemy.Boolean, default=True, name="operations")
    queue_all_runs = sqlalchemy.Column(sqlalchemy.Boolean, default=False, name="queue_all_runs")
    speculative_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=True, name="speculative_enabled")
    terraform_version = sqlalchemy.Column(sqlalchemy.String, default=None, name="terraform_version")
    trigger_prefixes = sqlalchemy.Column(sqlalchemy.String, default=None, name="trigger_prefixes")
    trigger_patterns = sqlalchemy.Column(sqlalchemy.String, default=None, name="trigger_patterns")
    vcs_repo = sqlalchemy.Column(sqlalchemy.String, default=None, name="vcs_repo")
    vcs_repo_oath_token_id = None
    vcs_repo_branch = sqlalchemy.Column(sqlalchemy.String, default=None, name="vcs_repo_branch")
    vcs_repo_ingress_submodules = sqlalchemy.Column(sqlalchemy.Boolean, default=False, name="vcs_repo_ingress_submodules")
    vcs_repo_identifier = sqlalchemy.Column(sqlalchemy.String, default=None, name="vcs_repo_identifier")
    vcs_repo_tags_regex = sqlalchemy.Column(sqlalchemy.String, default=None, name="vcs_repo_tags_regex")
    working_directory = sqlalchemy.Column(sqlalchemy.String, default=None, name="working_directory")
    assessments_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=False, name="assessments_enabled")
