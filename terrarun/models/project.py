# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import json
import re
import sqlalchemy
import sqlalchemy.orm
from sqlalchemy import func
from terrarun.api_error import ApiError
from terrarun.models.authorised_repo import AuthorisedRepo

from terrarun.models.base_object import BaseObject
from terrarun.database import Base, Database
import terrarun.database
from terrarun.models.configuration import ConfigurationVersion
from terrarun.models.ingress_attribute import IngressAttribute
from terrarun.models.oauth_token import OauthToken
from terrarun.models.run import Run
from terrarun.models.tool import Tool, ToolType
from terrarun.models.workspace import Workspace
from terrarun.workspace_execution_mode import WorkspaceExecutionMode
import terrarun.config


class Project(Base, BaseObject):

    ID_PREFIX = 'prj'
    MINIMUM_NAME_LENGTH = 3
    RESERVED_NAMES = []

    __tablename__ = 'project'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    api_id_fk = sqlalchemy.Column(sqlalchemy.ForeignKey("api_id.id"), nullable=True)
    api_id_obj = sqlalchemy.orm.relation("ApiId", foreign_keys=[api_id_fk])

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
    tool_id = sqlalchemy.Column(sqlalchemy.ForeignKey("tool.id"), nullable=True)
    tool = sqlalchemy.orm.relationship("Tool")
    _trigger_prefixes = sqlalchemy.Column(terrarun.database.Database.GeneralString, default=None, name="trigger_prefixes")
    _trigger_patterns = sqlalchemy.Column(terrarun.database.Database.GeneralString, default=None, name="trigger_patterns")

    authorised_repo_id = sqlalchemy.Column(
        sqlalchemy.ForeignKey("authorised_repo.id", name="fk_project_authorised_repo_id_authorised_repo_id"),
        nullable=True
    )
    authorised_repo = sqlalchemy.orm.relationship("AuthorisedRepo", back_populates="projects")
    vcs_repo_branch = sqlalchemy.Column(terrarun.database.Database.GeneralString, default=None, name="vcs_repo_branch")
    vcs_repo_ingress_submodules = sqlalchemy.Column(sqlalchemy.Boolean, default=False, name="vcs_repo_ingress_submodules")
    vcs_repo_tags_regex = sqlalchemy.Column(terrarun.database.Database.GeneralString, default=None, name="vcs_repo_tags_regex")
    working_directory = sqlalchemy.Column(terrarun.database.Database.GeneralString, default=None, name="working_directory")
    assessments_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=False, name="assessments_enabled")

    agent_pool_permissions = sqlalchemy.orm.relation("AgentPoolProjectPermission", back_populates="project")
    agent_pool_associations = sqlalchemy.orm.relation("AgentPoolProjectAssociation", back_populates="project")

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

    @property
    def trigger_patterns(self):
        """Return trigger prefixes"""
        if not self._trigger_patterns:
            return None
        return json.loads(self._trigger_patterns)

    @trigger_patterns.setter
    def trigger_patterns(self, val):
        """Return trigger prefixes"""
        if not val:
            self._trigger_patterns = None
            return
        self._trigger_patterns = json.dumps(val)

    @property
    def trigger_prefixes(self):
        """Return trigger prefixes"""
        if not self._trigger_prefixes:
            return None
        return json.loads(self._trigger_prefixes)

    @trigger_prefixes.setter
    def trigger_prefixes(self, val):
        """Return trigger prefixes"""
        if not val:
            self._trigger_prefixes = None
            return
        self._trigger_prefixes = json.dumps(val)

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
            for lifecycle_environment_group in new_lifecycle.lifecycle_environment_groups
            for lifecycle_environment in lifecycle_environment_group.lifecycle_environments
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

    def get_ingress_attributes(self, api_request):
        """Obtain all ingress attributes, with filter API query"""
        session = Database.get_session()
        # Investigate filtering by configuration versions that
        # have at least 1 run associated
        query = session.query(
            IngressAttribute,
        ).join(
            ConfigurationVersion
        ).join(
            Workspace
        ).join(
            Project
        ).outerjoin(
            Run,
            ConfigurationVersion.id==Run.configuration_version_id
        ).filter(
            Project.id==self.id
        )
        query = api_request.limit_query(query)
        return query.all()

    def check_vcs_repo_update_from_request(self, vcs_repo_attributes):
        """Update VCS repo from request"""
        # Check if VCS is defined in project
        if 'oauth-token-id' not in vcs_repo_attributes or 'identifier' not in vcs_repo_attributes:
            return {}, []

        new_oauth_token_id = vcs_repo_attributes['oauth-token-id']
        new_vcs_identifier = vcs_repo_attributes['identifier']

        # If both settings are present and have been cleared, unset repo
        if not new_oauth_token_id and not new_vcs_identifier:
            return {"authorised_repo": None}, []

        # Check if any child workspaces have a repository set
        errors = []
        for workspace in self.workspaces:
            if workspace.workspace_authorised_repo:
                errors.append(ApiError(
                    "Child workspace has a VCS repository configured",
                    f"A child workspace: {workspace.name} has a VCS repo configured",
                    "/data/attributes/vcs-repo"
                ))
        if errors:
            return {}, errors

        # Otherwise, attempt to get oauth token and authorised repo
        oauth_token = OauthToken.get_by_api_id(new_oauth_token_id)
        # If oauth token does not exist or is not associated to organisation, return error
        if (not oauth_token) or oauth_token.oauth_client.organisation != self.organisation:
            return {}, [ApiError(
                "invalid attribute", "Oauth token does not exist", "/data/attributes/vcs-repo/oauth-token-id"
            )]

        authorised_repo = AuthorisedRepo.get_by_external_id(
            oauth_token=oauth_token, external_id=new_vcs_identifier)
        if not authorised_repo:
            return {}, [ApiError(
                "invalid attribute", "Authorized repo does not exist", "/data/attributes/vcs-repo/identifier"
            )]

        return {"authorised_repo": authorised_repo}, []

    def update_attributes_from_request(self, attributes):
        """Update attributes from request"""
        update_kwargs = {}
        errors = []
        if "name" in attributes and attributes.get("name") != self.name:
            if self.validate_new_name(self.organisation, name=attributes.get("name")):
                update_kwargs["name"] = attributes.get("name")
            else:
                errors.append("Name is invalid", "Name either already exists or is invalid", "/data/attributes/name")

        if "variables" in attributes:
            update_kwargs["variables"] = json.dumps(attributes.get("variables"))

        if "terraform-version" in attributes:
            tool = None
            if attributes["terraform-version"]:
                tool = Tool.get_by_version(tool_type=ToolType.TERRAFORM_VERSION, version=attributes["terraform-version"])
                if not tool:
                    errors.append(ApiError(
                        'Invalid tool version',
                        'The tool version is invalid or the tool version does not exist.',
                        pointer='/data/attributes/terraform-version'
                    ))
            update_kwargs["tool"] = tool

        if "vcs-repo" in attributes:
            vcs_repo_kwargs, vcs_repo_errors = self.check_vcs_repo_update_from_request(
                vcs_repo_attributes=attributes["vcs-repo"]
            )
            errors += vcs_repo_errors
            update_kwargs.update(vcs_repo_kwargs)

            if attributes["vcs-repo"] is not None:
                if "tags-regex" in attributes["vcs-repo"]:
                    update_kwargs["vcs_repo_tags_regex"] = attributes["vcs-repo"]["tags-regex"]

                if "branch" in attributes["vcs-repo"]:
                    update_kwargs["vcs_repo_branch"] = attributes["vcs-repo"]["branch"]

            if "trigger-patterns" in attributes:
                update_kwargs["trigger_patterns"] = attributes["trigger-patterns"]

            if "trigger-prefixes" in attributes:
                update_kwargs["trigger_prefixes"] = attributes["trigger-prefixes"]

        # Handle update of execution mode
        if "execution-mode" in attributes:
            try:
                execution_mode = WorkspaceExecutionMode(attributes["execution-mode"])
                update_kwargs["execution_mode"] = execution_mode
            except ValueError:
                errors.append(ApiError(
                    "Execution mode is invalid",
                    "The value provided for execution mode is invalid",
                    "/data/attributes/execution-mode"
                ))

        # If any errors have been found, return early
        # before updating any attributes
        if errors:
            return errors

        # Update attributes and return without errors
        self.update_attributes(
            **update_kwargs
        )
        return []

    def get_api_details(self, api_request=None):
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
                "terraform-version": self.tool.version if self.tool else None,
                "trigger-prefixes": self.trigger_prefixes,
                "trigger-patterns": self.trigger_patterns,
                "updated-at": "2021-08-16T18:54:06.874Z",
                "vcs-repo": {
                    "branch": self.vcs_repo_branch,
                    "ingress-submodules": self.vcs_repo_ingress_submodules,
                    "tags-regex": self.vcs_repo_tags_regex,
                    "identifier": self.authorised_repo.external_id,
                    "display-identifier": self.authorised_repo.display_identifier,
                    "oauth-token-id": self.authorised_repo.oauth_token.api_id,
                    "webhook-url": f"{terrarun.config.Config().BASE_URL}/webhooks/vcs/{self.authorised_repo.webhook_id}",
                    "repository-http-url": self.authorised_repo.http_url,
                    "service-provider": self.authorised_repo.oauth_token.oauth_client.service_provider.value
                } if self.authorised_repo else None,
                "vcs-repo-identifier": self.authorised_repo.display_identifier if self.authorised_repo else None,
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

