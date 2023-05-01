# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from enum import Enum
import re
import sqlalchemy
import sqlalchemy.orm

from terrarun.models.base_object import BaseObject
from terrarun.config import Config
import terrarun.models.organisation
from terrarun.permissions.workspace import WorkspacePermissions
import terrarun.models.run
import terrarun.models.configuration
from terrarun.workspace_execution_mode import WorkspaceExecutionMode
import terrarun.models.workspace_task
import terrarun.models.user
from terrarun.database import Base, Database
from terrarun.models.workspace_tag import WorkspaceTag
import terrarun.database


class Workspace(Base, BaseObject):

    ID_PREFIX = 'ws'
    RESERVED_NAMES = ['setttings', 'projects']
    MINIMUM_NAME_LENGTH = 3

    __tablename__ = 'workspace'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(terrarun.database.Database.GeneralString, default=None)
    _description = sqlalchemy.Column(terrarun.database.Database.GeneralString, default=None, name="description")

    organisation_id = sqlalchemy.Column(sqlalchemy.ForeignKey("organisation.id"), nullable=False)
    organisation = sqlalchemy.orm.relationship("Organisation", back_populates="workspaces")

    enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=True, nullable=False)

    project_id = sqlalchemy.Column(
        sqlalchemy.ForeignKey("project.id", name="workspace_project_id_project_id"),
        nullable=False)
    project = sqlalchemy.orm.relationship("Project", back_populates="workspaces")

    environment_id = sqlalchemy.Column(
        sqlalchemy.ForeignKey("environment.id", name="fk_workspace_environment_id_environment_id"),
        nullable=False)
    environment = sqlalchemy.orm.relationship("Environment", back_populates="workspaces")

    state_versions = sqlalchemy.orm.relation("StateVersion", back_populates="workspace")
    configuration_versions = sqlalchemy.orm.relation("ConfigurationVersion", back_populates="workspace")

    team_accesses = sqlalchemy.orm.relationship("TeamWorkspaceAccess", back_populates="workspace")

    tags = sqlalchemy.orm.relationship("Tag", secondary="workspace_tag", back_populates="workspaces")

    workspace_tasks = sqlalchemy.orm.relationship("WorkspaceTask", back_populates="workspace")

    _allow_destroy_plan = sqlalchemy.Column(sqlalchemy.Boolean, default=None, name="allow_destroy_plan")
    _auto_apply = sqlalchemy.Column(sqlalchemy.Boolean, default=None, name="auto_apply")
    _execution_mode = sqlalchemy.Column(sqlalchemy.Enum(WorkspaceExecutionMode), nullable=True, default=None, name="execution_mode")
    _file_triggers_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=None, name="file_triggers_enabled")
    _global_remote_state = sqlalchemy.Column(sqlalchemy.Boolean, default=None, name="global_remote_state")
    _operations = sqlalchemy.Column(sqlalchemy.Boolean, default=None, name="operations")
    _queue_all_runs = sqlalchemy.Column(sqlalchemy.Boolean, default=None, name="queue_all_runs")
    _speculative_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=None, name="speculative_enabled")
    _terraform_version = sqlalchemy.Column(terrarun.database.Database.GeneralString, default=None, name="terraform_version")
    _trigger_prefixes = sqlalchemy.Column(terrarun.database.Database.GeneralString, default=None, name="trigger_prefixes")
    _trigger_patterns = sqlalchemy.Column(terrarun.database.Database.GeneralString, default=None, name="trigger_patterns")
    _vcs_repo = sqlalchemy.Column(terrarun.database.Database.GeneralString, default=None, name="vcs_repo")
    _vcs_repo_oath_token_id = None
    _vcs_repo_branch = sqlalchemy.Column(terrarun.database.Database.GeneralString, default=None, name="vcs_repo_branch")
    _vcs_repo_ingress_submodules = sqlalchemy.Column(sqlalchemy.Boolean, default=None, name="vcs_repo_ingress_submodules")
    _vcs_repo_identifier = sqlalchemy.Column(terrarun.database.Database.GeneralString, default=None, name="vcs_repo_identifier")
    _vcs_repo_tags_regex = sqlalchemy.Column(terrarun.database.Database.GeneralString, default=None, name="vcs_repo_tags_regex")
    _working_directory = sqlalchemy.Column(terrarun.database.Database.GeneralString, default=None, name="working_directory")
    _assessments_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=None, name="assessments_enabled")

    _latest_state = None
    _latest_configuration_version = None
    _latest_run = None

    @classmethod
    def get_by_organisation_and_name(cls, organisation, workspace_name):
        """Return organisation object, if it exists within an organisation, by name."""
        session = Database.get_session()
        ws = session.query(Workspace).filter(
            Workspace.name==workspace_name,
            Workspace.organisation==organisation
        ).first()
        return ws

    @classmethod
    def validate_new_name(cls, organisation, name):
        """Ensure organisation does not already exist and name isn't reserved"""
        session = Database.get_session()
        existing_workspace = session.query(cls).filter(cls.name==name, cls.organisation==organisation).first()
        if existing_workspace:
            return False
        if name in cls.RESERVED_NAMES:
            return False
        if len(name) < cls.MINIMUM_NAME_LENGTH:
            return False
        if not re.match(r'^[a-zA-Z0-9-_]+$', name):
            return False
        return True

    @classmethod
    def create(cls, organisation, project, environment):
        ws = cls(organisation=organisation, project=project, environment=environment)
        session = Database.get_session()
        ws.reset_name()
        session.add(ws)
        session.commit()
        return ws

    def reset_name(self):
        """Reset name of workspace, based on project name and environment name"""
        self.name = f"{self.project.name}-{self.environment.name}"

    def add_tag(self, tag):
        """Add tag to list of tags"""
        if tag not in self.tags:
            self.tags.append(tag)
            session = Database.get_session()
            session.add(self)
            session.commit()

    @property
    def runs(self):
        """Return runs for workspace"""
        runs = []
        for cv in self.configuration_versions:
            runs += cv.runs
        return runs

    @property
    def latest_configuration_version(self):
        """Return latest configuration version."""
        if self.configuration_versions:
            return self.configuration_versions[-1]
        return None

    @property
    def latest_state(self):
        """Return latest state version"""
        if self.state_versions:
            return self.state_versions[-1]
        return None

    @property
    def latest_run(self):
        """Return latest state version"""
        session = Database.get_session()
        run = session.query(
            terrarun.models.run.Run
        ).join(
            terrarun.models.configuration.ConfigurationVersion
        ).filter(
            terrarun.models.configuration.ConfigurationVersion.workspace == self
        ).order_by(
            terrarun.models.run.Run.created_at.desc()
        ).first()
        return run

    @property
    def description(self):
        """Return description"""
        if self._description is not None:
            return self._description
        return self.project.description

    @description.setter
    def description(self, value):
        """Set description, default to None, if non-truthful value."""
        self._description = value if value else None

    @property
    def allow_destroy_plan(self):
        """Return allow_destroy_plan"""
        if self._allow_destroy_plan is not None:
            return self._allow_destroy_plan
        return self.project.allow_destroy_plan

    @allow_destroy_plan.setter
    def allow_destroy_plan(self, value):
        """Set allow_destroy_plan"""
        self._allow_destroy_plan = value

    @property
    def auto_apply(self):
        """Return auto_apply"""
        if self._auto_apply is not None:
            return self._auto_apply
        return self.project.auto_apply

    @auto_apply.setter
    def auto_apply(self, value):
        """Set auto_apply"""
        self._auto_apply = value

    @property
    def execution_mode(self):
        """Return execution_mode"""
        if self._execution_mode is not None:
            return self._execution_mode
        return self.project.execution_mode

    @execution_mode.setter
    def execution_mode(self, value):
        """Set execution_mode"""
        self._execution_mode = value

    @property
    def file_triggers_enabled(self):
        """Return file_triggers_enabled"""
        if self._file_triggers_enabled is not None:
            return self._file_triggers_enabled
        return self.project.file_triggers_enabled

    @file_triggers_enabled.setter
    def file_triggers_enabled(self, value):
        """Set file_triggers_enabled"""
        self._file_triggers_enabled = value

    @property
    def global_remote_state(self):
        """Return file_triggers_enabled"""
        if self._global_remote_state is not None:
            return self._global_remote_state
        return self.project.global_remote_state

    @global_remote_state.setter
    def global_remote_state(self, value):
        """Set global_remote_state"""
        self._global_remote_state = value

    @property
    def operations(self):
        """Return operations"""
        if self._operations is not None:
            return self._operations
        return self.project.operations

    @operations.setter
    def operations(self, value):
        """Set operations"""
        self._operations = value

    @property
    def queue_all_runs(self):
        """Return queue_all_runs"""
        if self._queue_all_runs is not None:
            return self._queue_all_runs
        return self.project.queue_all_runs

    @queue_all_runs.setter
    def queue_all_runs(self, value):
        """Set queue_all_runs"""
        self._queue_all_runs = value

    @property
    def speculative_enabled(self):
        """Return speculative_enabled"""
        if self._speculative_enabled is not None:
            return self._speculative_enabled
        return self.project.speculative_enabled

    @speculative_enabled.setter
    def speculative_enabled(self, value):
        """Set speculative_enabled"""
        self._speculative_enabled = value

    @property
    def terraform_version(self):
        """Return terraform_version"""
        if self._terraform_version is not None:
            return self._terraform_version
        return self.project.terraform_version

    @terraform_version.setter
    def terraform_version(self, value):
        """Set terraform_version"""
        self._terraform_version = value if value else None

    @property
    def trigger_prefixes(self):
        """Return trigger_prefixes"""
        if self._trigger_prefixes is not None:
            return self._trigger_prefixes
        return self.project.trigger_prefixes

    @trigger_prefixes.setter
    def trigger_prefixes(self, value):
        """Set trigger_prefixes"""
        self._trigger_prefixes = value if value else None

    @property
    def trigger_patterns(self):
        """Return trigger_patterns"""
        if self._trigger_patterns is not None:
            return self._trigger_patterns
        return self.project.trigger_patterns

    @trigger_patterns.setter
    def trigger_patterns(self, value):
        """Set trigger_patterns"""
        self._trigger_patterns = value if value else None

    @property
    def vcs_repo(self):
        """Return vcs_repo"""
        if self._vcs_repo is not None:
            return self._vcs_repo
        return self.project.vcs_repo

    @vcs_repo.setter
    def vcs_repo(self, value):
        """Set vcs_repo"""
        self._vcs_repo = value if value else None

    @property
    def vcs_repo_oath_token_id(self):
        """Return vcs_repo_oath_token_id"""
        if self._vcs_repo_oath_token_id is not None:
            return self._vcs_repo_oath_token_id
        return self.project.vcs_repo_oath_token_id

    @vcs_repo_oath_token_id.setter
    def vcs_repo_oath_token_id(self, value):
        """Set vcs_repo_oath_token_id"""
        self._vcs_repo_oath_token_id = value if value else None

    @property
    def vcs_repo_branch(self):
        """Return vcs_repo_branch"""
        if self._vcs_repo_branch is not None:
            return self._vcs_repo_branch
        return self.project.vcs_repo_branch

    @vcs_repo_branch.setter
    def vcs_repo_branch(self, value):
        """Set vcs_repo_branch"""
        self._vcs_repo_branch = value if value else None

    @property
    def vcs_repo_ingress_submodules(self):
        """Return vcs_repo_ingress_submodules"""
        if self._vcs_repo_ingress_submodules is not None:
            return self._vcs_repo_ingress_submodules
        return self.project.vcs_repo_ingress_submodules

    @vcs_repo_ingress_submodules.setter
    def vcs_repo_ingress_submodules(self, value):
        """Set vcs_repo_ingress_submodules"""
        self._vcs_repo_ingress_submodules = value

    @property
    def vcs_repo_identifier(self):
        """Return vcs_repo_identifier"""
        if self._vcs_repo_identifier is not None:
            return self._vcs_repo_identifier
        return self.project.vcs_repo_identifier

    @vcs_repo_identifier.setter
    def vcs_repo_identifier(self, value):
        """Set vcs_repo_identifier"""
        self._vcs_repo_identifier = value if value else None

    @property
    def vcs_repo_tags_regex(self):
        """Return vcs_repo_tags_regex"""
        if self._vcs_repo_tags_regex is not None:
            return self._vcs_repo_tags_regex
        return self.project.vcs_repo_tags_regex

    @vcs_repo_tags_regex.setter
    def vcs_repo_tags_regex(self, value):
        """Set vcs_repo_tags_regex"""
        self._vcs_repo_tags_regex = value if value else None

    @property
    def working_directory(self):
        """Return working_directory"""
        if self._working_directory is not None:
            return self._working_directory
        return self.project.working_directory

    @working_directory.setter
    def working_directory(self, value):
        """Set working_directory"""
        self._working_directory = value if value else None

    @property
    def assessments_enabled(self):
        """Return assessments_enabled"""
        if self._assessments_enabled is not None:
            return self._assessments_enabled
        return self.project.assessments_enabled

    @assessments_enabled.setter
    def assessments_enabled(self, value):
        """Set assessments_enabled"""
        self._assessments_enabled = value

    def associate_task(
            self,
            task: terrarun.models.workspace_task.WorkspaceTaskEnforcementLevel,
            enforcement_level: terrarun.models.workspace_task.WorkspaceTaskEnforcementLevel,
            stage: terrarun.models.workspace_task.WorkspaceTaskStage):
        """Associate a task with the workspace"""
        workspace_task = terrarun.models.workspace_task.WorkspaceTask(
            workspace=self,
            task=task,
            enforcement_level=enforcement_level,
            stage=stage
        )
        session = Database.get_session()
        session.add(workspace_task)
        session.commit()
        return workspace_task

    def get_api_details(self, effective_user: terrarun.models.user.User):
        """Return details for workspace."""
        workspace_permissions = WorkspacePermissions(current_user=effective_user, workspace=self)
        return {
            "attributes": {
                "actions": {
                    "is-destroyable": True
                },
                "allow-destroy-plan": self.allow_destroy_plan,
                "apply-duration-average": 158000,
                "auto-apply": self.auto_apply,
                "auto-destroy-at": None,
                "created-at": "2021-06-03T17:50:20.307Z",
                "description": self.description,
                "environment": self.environment.name,
                "execution-mode": self.execution_mode.value,
                "file-triggers-enabled": self.file_triggers_enabled,
                "global-remote-state": self.global_remote_state,
                "latest-change-at": "2021-06-23T17:50:48.815Z",
                "locked": False,
                "name": self.name,
                "operations": self.operations,
                "permissions": workspace_permissions.get_api_permissions(),
                "plan-duration-average": 20000,
                "policy-check-failures": None,
                "queue-all-runs": self.queue_all_runs,
                "resource-count": 0,
                "run-failures": 6,
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
                "working-directory": self.working_directory,
                "workspace-kpis-runs-count": 7
            },
            "id": self.api_id,
            "links": {
                "self": f"/api/v2/organizations/{self.organisation.name}/workspaces/{self.name}"
            },
            "relationships": {
                "agent-pool": {
                    "data": {
                        "id": "apool-QxGd2tRjympfMvQc",
                        "type": "agent-pools"
                    }
                },
                "current-configuration-version": {
                    "data": {
                        "id": self.latest_configuration_version.api_id,
                        "type": "configuration-versions"
                    },
                    "links": {
                        "related": f"/api/v2/configuration-versions/{self.latest_configuration_version.api_id}"
                    }
                } if self.latest_configuration_version else {},
                "current-run": {
                    "data": {
                        "id": "run-UyCw2TDCmxtfdjmy",
                        "type": "runs"
                    },
                    "links": {
                        "related": "/api/v2/runs/run-UyCw2TDCmxtfdjmy"
                    }
                },
                "current-state-version": {
                    "data": {
                        "id": self.latest_state.api_id,
                        "type": "state-versions"
                    },
                    "links": {
                        "related": f"/api/v2/workspaces/{self.api_id}/current-state-version"
                    }
                } if self.latest_state else {},
                "latest-run": {
                    "data": {
                        "id": self.latest_run.api_id,
                        "type": "runs"
                    },
                    "links": {
                        "related": f"/api/v2/runs/{self.latest_run.api_id}"
                    }
                } if self._latest_run else {},
                "organization": {
                    "data": {
                        "id": self.organisation.name,
                        "type": "organizations"
                    }
                },
                "outputs": {
                    "data": []
                },
                "tags": {
                    "data": [tag.get_relationship() for tag in self.tags]
                },
                "readme": {
                    "data": {
                        "id": "227247",
                        "type": "workspace-readme"
                    }
                },
                "remote-state-consumers": {
                    "links": {
                        "related": "/api/v2/workspaces/ws-qPhan8kDLymzv2uS/relationships/remote-state-consumers"
                    }
                }
            },
            "type": "workspaces"
        }
