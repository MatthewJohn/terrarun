# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import re
import sqlalchemy
import sqlalchemy.orm

from terrarun.base_object import BaseObject
from terrarun.database import Base, Database
import terrarun.database
from terrarun.workspace import Workspace
from terrarun.workspace_execution_mode import WorkspaceExecutionMode


class Project(Base, BaseObject):

    ID_PREFIX = 'mws'
    MINIMUM_NAME_LENGTH = 3
    RESERVED_NAMES = []

    __tablename__ = 'project'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=False)
    description = sqlalchemy.Column(terrarun.database.Database.GeneralString)

    organisation_id = sqlalchemy.Column(sqlalchemy.ForeignKey(
        "organisation.id", name="fk_project_organisation_id_organisation_id"),
        nullable=False)
    organisation = sqlalchemy.orm.relationship("Organisation", back_populates="projects")

    workspaces = sqlalchemy.orm.relation("Workspace", back_populates="project")

    lifecycle_id = sqlalchemy.Column(
        sqlalchemy.ForeignKey("lifecycle.id", name="fk_project_lifecycle_id_lifecycle_id"),
        nullable=False)
    lifecycle = sqlalchemy.orm.relationship("Lifecycle", back_populates="projects")

    allow_destroy_plan = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    auto_apply = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    execution_mode = sqlalchemy.Column(sqlalchemy.Enum(WorkspaceExecutionMode), nullable=True, default=WorkspaceExecutionMode.REMOTE)
    file_triggers_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=True, name="file_triggers_enabled")
    global_remote_state = sqlalchemy.Column(sqlalchemy.Boolean, default=False, name="global_remote_state")
    operations = sqlalchemy.Column(sqlalchemy.Boolean, default=True, name="operations")
    queue_all_runs = sqlalchemy.Column(sqlalchemy.Boolean, default=False, name="queue_all_runs")
    speculative_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=True, name="speculative_enabled")
    terraform_version = sqlalchemy.Column(terrarun.database.Database.GeneralString, default=None, name="terraform_version")
    trigger_prefixes = sqlalchemy.Column(terrarun.database.Database.GeneralString, default=None, name="trigger_prefixes")
    trigger_patterns = sqlalchemy.Column(terrarun.database.Database.GeneralString, default=None, name="trigger_patterns")
    vcs_repo = sqlalchemy.Column(terrarun.database.Database.GeneralString, default=None, name="vcs_repo")
    vcs_repo_oath_token_id = None
    vcs_repo_branch = sqlalchemy.Column(terrarun.database.Database.GeneralString, default=None, name="vcs_repo_branch")
    vcs_repo_ingress_submodules = sqlalchemy.Column(sqlalchemy.Boolean, default=False, name="vcs_repo_ingress_submodules")
    vcs_repo_identifier = sqlalchemy.Column(terrarun.database.Database.GeneralString, default=None, name="vcs_repo_identifier")
    vcs_repo_tags_regex = sqlalchemy.Column(terrarun.database.Database.GeneralString, default=None, name="vcs_repo_tags_regex")
    working_directory = sqlalchemy.Column(terrarun.database.Database.GeneralString, default=None, name="working_directory")
    assessments_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=False, name="assessments_enabled")

    @classmethod
    def get_by_name(cls, organisation, name):
        """Return project by organisation and name"""
        session = Database.get_session()
        return session.query(
            cls
        ).filter(
            cls.organisation == organisation,
            cls.name == name
        ).first()

    @classmethod
    def validate_new_name(cls, organisation, name):
        """Ensure project does not already exist and name isn't reserved"""
        # Ensure name doesn't contain invalid characters
        if not re.match(r'^[A-Za-z0-9][A-Za-z0-9-_]+[A-Za-z0-9]$', name):
            return False

        if cls.get_by_name(organisation, name):
            return False
        if name in cls.RESERVED_NAMES:
            return False
        if len(name) < cls.MINIMUM_NAME_LENGTH:
            return False
        return True

    @classmethod
    def create(cls, organisation, name, lifecycle, **kwargs):
        """Create project"""
        if not cls.validate_new_name(organisation, name):
            return None

        project = cls(organisation=organisation, name=name, lifecycle=lifecycle, **kwargs)
        session = Database.get_session()
        session.add(project)
        session.commit()

        project.switch_lifecyce(lifecycle)

        return project

    def update_attributes(self, session=None, **kwargs):
        """Determine if lifecycle is being updated."""
        # Check for change in lifecycle
        if ('lifecycle' in kwargs and
                (self.lifecycle is None or
                 kwargs['lifecycle'] is None or
                kwargs['lifecycle'].id != self.lifecycle.id)):

            self.switch_lifecyce(kwargs['lifecycle'])

        return super().update_attributes(session, **kwargs)

    def switch_lifecyce(self, new_lifecycle):
        """Update lifecycle of project, adjusting workspaces."""
        # Create list of all environments that exist in new lifecycle
        new_environments = [
            lifecycle_environment.environment
            for lifecycle_environment in new_lifecycle.get_lifecycle_environments()
        ] if new_lifecycle else []

        # Iterate through all workspaces for project,
        # disabling those that are not part of the new lifecycle
        # and enabling/creating those that are.
        for workspace in self.workspaces:
            if workspace.environment in new_environments:
                workspace.update_attributes(enabled=True)
                new_environments.remove(new_environments)
            else:
                workspace.update_attributes(enabled=False)

        # Create workspaces for each of the missing new environments
        for new_environment in new_environments:
            workspace = Workspace.create(
                organisation=self.organisation,
                project=self,
                environment=new_environment
            )

    def get_api_details(self):
        """Return details for workspace."""
        return {
            "attributes": {
                "allow-destroy-plan": self.allow_destroy_plan,
                "auto-apply": self.auto_apply,
                "created-at": "2021-06-03T17:50:20.307Z",
                "description": self.description,
                "execution-mode": self.execution_mode.value,
                "file-triggers-enabled": self.file_triggers_enabled,
                "global-remote-state": self.global_remote_state,
                "latest-change-at": "2021-06-23T17:50:48.815Z",
                "name": self.name,
                "operations": self.operations,
                "queue-all-runs": self.queue_all_runs,
                "source": "terraform",
                "source-name": None,
                "source-url": None,
                "speculative-enabled": self.speculative_enabled,
                "structured-run-output-enabled": False,
                "terraform-version": self.terraform_version,
                "trigger-prefixes": [],
                "updated-at": "2021-08-16T18:54:06.874Z",
                "vcs-repo": self.vcs_repo,
                "vcs-repo-identifier": self.vcs_repo_identifier,
                "working-directory": self.working_directory
            },
            "id": self.api_id,
            "links": {
                "self": f"/api/v2/projects/{self.api_id}"
            },
            "relationships": {
                "organization": {
                    "data": {
                        "id": self.organisation.name,
                        "type": "organizations"
                    }
                },
                "workspaces": {
                    "data": [
                        {
                            "id": workspace.api_id,
                            "type": "workspaces"
                        }
                        for workspace in self.workspaces
                    ]
                }
            },
            "type": "projects"
        }

