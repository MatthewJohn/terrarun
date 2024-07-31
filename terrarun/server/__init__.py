# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

import base64
import json
import re
from time import sleep

from flask import Flask, make_response, request, session
from flask.signals import request_finished
import flask
from flask_cors import CORS
from flask_restful import Api, Resource, reqparse
from ansi2html import Ansi2HTMLConverter
from terrarun.api_request import ApiRequest
from terrarun.errors import InvalidVersionNumberError, ToolChecksumUrlPlaceholderError, ToolUrlPlaceholderError, UnableToDownloadToolArchiveError, UnableToDownloadToolChecksumFileError

from terrarun.job_processor import JobProcessor
import terrarun.config
from terrarun.models import workspace
from terrarun.models.agent import Agent, AgentStatus
from terrarun.models.agent_pool import AgentPool
from terrarun.models.agent_token import AgentToken
from terrarun.models.apply import Apply
from terrarun.models.audit_event import AuditEvent
from terrarun.models.configuration import ConfigurationVersion
from terrarun.database import Database
from terrarun.models.github_app_oauth_token import GithubAppOauthToken
from terrarun.models.ingress_attribute import IngressAttribute
from terrarun.models.lifecycle import Lifecycle
from terrarun.models.lifecycle_environment import LifecycleEnvironment
from terrarun.models.lifecycle_environment_group import LifecycleEnvironmentGroup
from terrarun.models.oauth_client import OauthClient, OauthServiceProvider
from terrarun.models.oauth_token import OauthToken
from terrarun.models.project import Project
from terrarun.models.organisation import Organisation
from terrarun.models.state_version_output import StateVersionOutput
from terrarun.models.tool import Tool, ToolType
from terrarun.permissions.organisation import OrganisationPermissions
from terrarun.permissions.user import UserPermissions
from terrarun.permissions.workspace import WorkspacePermissions
from terrarun.models.plan import Plan
from terrarun.models.run import Run
from terrarun.models.run_queue import JobQueueType
from terrarun.models.state_version import StateVersion
from terrarun.models.tag import Tag
from terrarun.models.task import Task
from terrarun.models.task_result import TaskResult, TaskResultStatus
from terrarun.models.task_stage import TaskStage
from terrarun.terraform_command import TerraformCommandState
from terrarun.models.user_token import UserToken, UserTokenType
from terrarun.models.workspace import Workspace
from terrarun.models.user import User
from terrarun.models.team_workspace_access import TeamWorkspaceRunsPermission, TeamWorkspaceStateVersionsPermissions
from terrarun.models.workspace_task import WorkspaceTask, WorkspaceTaskEnforcementLevel, WorkspaceTaskStage
from terrarun.models.environment import Environment
from terrarun.agent_filesystem import AgentFilesystem
from terrarun.presign import Presign
from terrarun.api_error import ApiError, api_error_response
from terrarun.server.authenticated_endpoint import AuthenticatedEndpoint
from terrarun.server.route_registration import RouteRegistration
from terrarun.server.routes import *
from terrarun.logger import get_logger
from terrarun.api_entities.base_entity import ListView
from terrarun.api_entities.organization import (
    OrganizationUpdateEntity, OrganizationView, OrganizationCreateEntity
)
from terrarun.api_entities.agent_pool import AgentPoolView


logger = get_logger(__name__)


class Server(object):
    """Manage web server and route requests"""

    def __init__(self, ssl_public_key=None, ssl_private_key=None):
        """Create flask app and store member variables"""
        self._app = Flask(
            __name__,
            static_folder='static',
            template_folder='templates'
        )
        self._cors = CORS(self._app)
        self._app.teardown_request(self.shutdown_session)

        self._api = Api(
            self._app,
        )

        self.host = '0.0.0.0'
        self.port = 5000
        self.ssl_public_key = ssl_public_key
        self.ssl_private_key = ssl_private_key

        self._register_routes()

    def shutdown_session(self, exception=None):
        """Tear down database session."""
        Database.get_session().remove()

    def _register_routes(self):
        """Register routes with flask."""

        # Terraform registry routes
        self._api.add_resource(
            ApiTerraformWellKnown,
            '/.well-known/terraform.json'
        )
        self._api.add_resource(
            ApiTerraformPing,
            '/api/v2/ping'
        )
        self._api.add_resource(
            ApiTerraformMotd,
            '/api/terraform/motd'
        )
        self._api.add_resource(
            ApiTerraformAccountDetails,
            '/api/v2/account/details'
        )

        self._api.add_resource(
            ApiTerraformOrganisation,
            '/api/v2/organizations'
        )
        self._api.add_resource(
            ApiTerraformOrganisationDetails,
            '/api/v2/organizations/<string:organisation_name>'
        )
        self._api.add_resource(
            ApiTerraformOrganisationEntitlementSet,
            '/api/v2/organizations/<string:organisation_name>/entitlement-set'
        )
        self._api.add_resource(
            ApiTerraformOrganisationWorkspaces,
            '/api/v2/organizations/<string:organisation_name>/workspaces'
        )
        self._api.add_resource(
            ApiTerraformWorkspace,
            '/api/v2/organizations/<string:organisation_name>/workspaces/<string:workspace_name>',
            '/api/v2/workspaces/<string:workspace_id>'
        )
        self._api.add_resource(
            ApiTerraformOrganisationWorkspaceRelationshipsProjects,
            '/api/v2/organizations/<string:organisation_name>/workspaces/<string:workspace_name>/relationships/projects'
        )
        self._api.add_resource(
            ApiTerraformOrganisationTasks,
            '/api/v2/organizations/<string:organisation_name>/tasks'
        )
        self._api.add_resource(
            ApiTerraformOrganisationQueue,
            '/api/v2/organizations/<string:organisation_name>/runs/queue'
        )
        self._api.add_resource(
            ApiTerraformOrganisationOauthClients,
            '/api/v2/organizations/<string:organisation_name>/oauth-clients'
        )

        self._api.add_resource(
            ApiTerraformOauthClient,
            '/api/v2/oauth-clients/<string:oauth_client_id>'
        )

        self._api.add_resource(
            ApiTerraformWorkspaceConfigurationVersions,
            '/api/v2/workspaces/<string:workspace_id>/configuration-versions'
        )
        self._api.add_resource(
            ApiTerraformWorkspaceLatestStateVersion,
            '/api/v2/workspaces/<string:workspace_id>/current-state-version'
        )
        self._api.add_resource(
            ApiTerraformWorkspaceLatestStateVersionOutputs,
            '/api/v2/workspaces/<string:workspace_id>/current-state-version-outputs'
        )
        self._api.add_resource(
            ApiTerraformWorkspaceStates,
            '/api/v2/workspaces/<string:workspace_id>/state-versions'
        )
        self._api.add_resource(
            ApiTerraformWorkspaceRelationshipsTags,
            '/api/v2/workspaces/<string:workspace_id>/relationships/tags'
        )
        self._api.add_resource(
            ApiTerraformWorkspaceActionsLock,
            '/api/v2/workspaces/<string:workspace_id>/actions/lock'
        )
        self._api.add_resource(
            ApiTerraformWorkspaceActionsUnlock,
            '/api/v2/workspaces/<string:workspace_id>/actions/unlock'
        )
        self._api.add_resource(
            ApiTerraformWorkspaceActionsForceUnlock,
            '/api/v2/workspaces/<string:workspace_id>/actions/force-unlock'
        )
        self._api.add_resource(
            ApiTerraformTaskDetails,
            '/api/v2/tasks/<string:task_id>'
        )
        self._api.add_resource(
            ApiTerraformConfigurationVersionUpload,
            '/api/v2/upload-configuration/<string:configuration_version_id>'
        )
        self._api.add_resource(
            ApiTerraformConfigurationVersions,
            '/api/v2/configuration-versions/<string:configuration_version_id>'
        )
        self._api.add_resource(
            ApiTerraformRunConfigurationVersionDownload,
            '/api/v2/runs/<string:run_id>/configuration-version/download'
        )
        self._api.add_resource(
            ApiTerraformRun,
            '/api/v2/runs',
            '/api/v2/runs/<string:run_id>'
        )
        self._api.add_resource(
            ApiTerraformRunRunEvents,
            '/api/v2/runs/<string:run_id>/run-events'
        )
        self._api.add_resource(
            ApiTerraformRunAuditEvents,
            '/api/v2/runs/<string:run_id>/relationships/audit-events'
        )
        self._api.add_resource(
            ApiTerraformRunTaskStages,
            '/api/v2/runs/<string:run_id>/task-stages'
        )
        self._api.add_resource(
            ApiTerraformTaskStage,
            '/api/v2/task-stages/<string:task_stage_id>'
        )
        self._api.add_resource(
            ApiTerraformRunActionsCancel,
            '/api/v2/runs/<string:run_id>/actions/cancel'
        )
        self._api.add_resource(
            ApiTerraformRunActionsDiscard,
            '/api/v2/runs/<string:run_id>/actions/discard'
        )
        self._api.add_resource(
            ApiTerraformWorkspaceRuns,
            '/api/v2/workspaces/<string:workspace_id>/runs'
        )
        self._api.add_resource(
            ApiTerraformWorkspaceTasks,
            '/api/v2/workspaces/<string:workspace_id>/tasks'
        )
        self._api.add_resource(
            ApiTerraformWorkspaceTask,
            '/api/v2/workspaces/<string:workspace_id>/tasks/<string:workspace_task_id>'
        )
        self._api.add_resource(
            ApiTerraformTaskResults,
            '/api/v2/task-results/<string:task_result_id>'
        )
        self._api.add_resource(
            ApiTerraformPlans,
            '/api/v2/plans',
            '/api/v2/plans/<string:plan_id>'
        )
        self._api.add_resource(
            ApiTerraformPlanLog,
            '/api/v2/plans/<string:plan_id>/log'
        )
        self._api.add_resource(
            ApiTerraformPlanJsonOutput,
            '/api/v2/plans/<string:plan_id>/json-output'
        )
        self._api.add_resource(
            ApiTerraformPlanJsonProvidersSchemas,
            '/api/v2/plans/<string:plan_id>/json-providers-schemas',
        )
        self._api.add_resource(
            ApiTerraformStateVersionDownload,
            '/api/v2/state-versions/<string:state_version_id>/download'
        )
        self._api.add_resource(
            ApiTerraformStateVersionOutput,
            '/api/v2/state-version-outputs/<string:state_version_output_id>'
        )
        self._api.add_resource(
            ApiTerraformIngressAttribute,
            '/api/v2/ingress-attributes/<string:ingress_attribute_id>'
        )
        self._api.add_resource(
            ApiTerraformApplyRun,
            '/api/v2/runs/<string:run_id>/actions/apply'
        )
        self._api.add_resource(
            ApiTerraformApplies,
            '/api/v2/applies/<string:apply_id>'
        )
        self._api.add_resource(
            ApiTerraformApplyLog,
            '/api/v2/applies/<string:apply_id>/log'
        )
        self._api.add_resource(
            ApiTerraformUserDetails,
            '/api/v2/users/<string:user_id>'
        )
        self._api.add_resource(
            ApiTerraformUserTokens,
            '/api/v2/users/<string:user_id>/authentication-tokens'
        )
        self._api.add_resource(
            ApiUserGithubAppOauthTokens,
            '/api/v2/users/<string:user_id>/github-app-oauth-tokens'
        )
        self._api.add_resource(
            ApiOauthTokenAuthorisedRepos,
            '/api/v2/oauth-tokens/<string:oauth_token_id>/authorized-repos'
        )

        # Custom Terrarun-specific endpoints
        self._api.add_resource(
            ApiTerraformOrganisationEnvironments,
            '/api/v2/organizations/<string:organisation_name>/environments'
        )
        self._api.add_resource(
            ApiTerraformEnvironment,
            '/api/v2/environments/<string:environment_id>'
        )
        self._api.add_resource(
            ApiTerraformEnvironmentLifecycleEnvironments,
            '/api/v2/environments/<string:environment_id>/lifecycle-environments'
        )
        # Custom Terrarun endpoint
        self._api.add_resource(
            ApiTerraformOrganisationProjects,
            '/api/v2/organizations/<string:organisation_name>/projects',
            '/api/v2/organizations/<string:organisation_name>/projects/<string:project_name>'
        )
        self._api.add_resource(
            ApiTerraformProject,
            '/api/v2/projects/<string:project_id>'
        )
        # Custom Terrarun endpoint
        self._api.add_resource(
            ApiTerrarunProjectIngressAttributes,
            '/api/v2/projects/<string:project_id>/ingress-attributes'
        )
        self._api.add_resource(
            ApiTerraformOrganisationLifecycles,
            '/api/v2/organizations/<string:organisation_name>/lifecycles'
        )
        self._api.add_resource(
            ApiTerraformOrganisationLifecycle,
            '/api/v2/organizations/<string:organisation_name>/lifecycles/<string:lifecycle_name>'
        )
        self._api.add_resource(
            ApiTerraformLifecycle,
            '/api/v2/lifecycles/<string:lifecycle_id>'
        )
        self._api.add_resource(
            ApiTerraformLifecycleLifecycleEnvironmentGroups,
            '/api/v2/lifecycles/<string:lifecycle_id>/lifecycle-environment-groups'
        )
        self._api.add_resource(
            ApiTerraformLifecycleEnvironmentGroup,
            '/api/v2/lifecycle-environment-groups/<string:lifecycle_environment_group_id>'
        )
        self._api.add_resource(
            ApiTerraformLifecycleEnvironmentGroupLifecycleEnvironments,
            '/api/v2/lifecycle-environment-groups/<string:lifecycle_environment_group_id>/lifecycle-environments'
        )
        self._api.add_resource(
            ApiTerraformLifecycleEnvironment,
            '/api/v2/lifecycle-environments/<string:lifecycle_environment_id>'
        )
        self._api.add_resource(
            ApiAuthenticate,
            '/api/terrarun/v1/authenticate'
        )
        self._api.add_resource(
            ApiTerrarunOrganisationCreateNameValidation,
            '/api/terrarun/v1/organisation/create/name-validation'
        )
        self._api.add_resource(
            ApiTerrarunWorkspaceCreateNameValidation,
            '/api/terrarun/v1/organisation/<string:organisation_name>/workspace-name-validate'
        )
        self._api.add_resource(
            ApiTerrarunProjectCreateNameValidation,
            '/api/terrarun/v1/organisation/<string:organisation_name>/project-name-validate'
        )
        self._api.add_resource(
            ApiTerrarunTaskCreateNameValidation,
            '/api/terrarun/v1/organisation/<string:organisation_name>/task-name-validate'
        )
        self._api.add_resource(
            ApiTerrarunEnvironmentCreateNameValidation,
            '/api/terrarun/v1/organisation/<string:organisation_name>/environment-name-validate'
        )
        self._api.add_resource(
            ApiTerrarunLifecycleCreateNameValidation,
            '/api/terrarun/v1/organisation/<string:organisation_name>/lifecycle-name-validate'
        )

        self._api.add_resource(
            ApiOrganisationAgentPoolList,
            '/api/v2/organizations/<string:organisation_name>/agent-pools'
        )
        self._api.add_resource(
            ApiOrganisationAgentPool,
            '/api/v2/agent-pools/<string:agent_pool_id>'
        )

        self._api.add_resource(
            ApiToolVersions,
            "/api/v2/tool-versions"
        )

        # VCS Oauth authorize
        self._api.add_resource(
            OauthAuthorise,
            '/auth/<string:callback_uuid>'
        )
        self._api.add_resource(
            OauthAuthoriseCallback,
            '/auth/<string:callback_uuid>/callback'
        )

        # Agent APIs
        self._api.add_resource(
            ApiAgentRegister,
            '/api/agent/register'
        )
        self._api.add_resource(
            ApiAgentStatus,
            '/api/agent/status'
        )
        self._api.add_resource(
            ApiAgentJobs,
            '/api/agent/jobs'
        )
        self._api.add_resource(
            ApiAgentPlanLog,
            "/api/agent/log/plan/<string:plan_id>"
        )
        self._api.add_resource(
            ApiAgentApplyLog,
            "/api/agent/log/apply/<string:apply_id>"
        )
        self._api.add_resource(
            ApiAgentFilesystem,
            "/api/agent/filesystem"
        )

        for child_route_class in RouteRegistration.__subclasses__():
            child_route_class().register_routes(self._app, self._api)

        def expire_session(sender, response, **extra):
            """Expire all DB objects when connection is closed"""
            session = Database.get_session()
            session.expire_all()
        request_finished.connect(expire_session, self._app)

    def run(self, debug=None):
        """Run flask server."""
        kwargs = {
            'host': self.host,
            'port': self.port,
            'debug': True,
            'threaded': True,
        }
        if self.ssl_public_key and self.ssl_private_key:
            kwargs['ssl_context'] = (self.ssl_public_key, self.ssl_private_key)

        self._app.secret_key = "abcefg"
        # Set cookie values
        self._app.config.update({
            'SESSION_COOKIE_SECURE': True,
            'SESSION_COOKIE_HTTPONLY': True,
            'SESSION_COOKIE_SAMESITE': 'Lax',
        })

        self._app.run(**kwargs)


class ApiAuthenticate(Resource):
    """Interface to authenticate user"""

    def post(self):
        """Authenticate user"""
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, location='json')
        parser.add_argument('password', type=str, location='json')
        args = parser.parse_args()
        user = User.get_by_username(args.username)

        if not user or not user.check_password(args.password):
            return {}, 403

        token = UserToken.create(user=user, type=UserTokenType.UI)

        # Set Authorization session token
        session['Authorization'] = token.token
        session.modified = True

        return {"data": token.get_creation_api_details()}


class ApiTerraformUserTokens(AuthenticatedEndpoint):
    """Get user tokens for user"""

    def check_permissions_get(self, user_id, current_user, current_job, *args, **kwargs):
        """Check if user has permission to modify user tokens"""
        target_user = User.get_by_api_id(user_id)
        # @TODO Do not return 403 when user does not exist
        if not target_user:
            return False
        return UserPermissions(current_user=current_user, user=target_user).check_permission(
            UserPermissions.Permissions.CAN_MANAGE_USER_TOKENS)

    def _get(self, user_id, current_user, current_job):
        """Return tokens for user"""
        user = User.get_by_api_id(user_id)
        if not user_id:
            return {}, 404
        return {
            "data": [
                user_token.get_api_details()
                for user_token in user.user_tokens
            ]
        }

    def check_permissions_post(self, current_user, current_job, user_id, *args, **kwargs):
        """Check if user has permission to modify user tokens"""
        target_user = User.get_by_api_id(user_id)
        # @TODO Do not return 403 when user does not exist
        if not target_user:
            return False
        return UserPermissions(current_user=current_user, user=target_user).check_permission(
            UserPermissions.Permissions.CAN_MANAGE_USER_TOKENS)

    def _post(self, current_user, current_job, user_id):
        """Create token"""
        user = User.get_by_api_id(user_id)
        if not user_id:
            return {}, 404

        description = flask.request.get_json().get('data', {}).get('attributes', {}).get('description', None)
        if not description:
            return {'Error': 'Missing description'}, 400

        user_token = UserToken.create(
            user=user, type=UserTokenType.USER_GENERATED,
            description=description
        )
        return {
            "data": user_token.get_creation_api_details()
        }


class ApiUserGithubAppOauthTokens(AuthenticatedEndpoint):
    """Get github app oauth tokens for user"""

    def check_permissions_get(self, user_id, current_user, current_job, *args, **kwargs):
        """Check if user has permission to modify user tokens"""
        target_user = User.get_by_api_id(user_id)
        # @TODO Do not return 403 when user does not exist
        if not target_user:
            return False
        return UserPermissions(current_user=current_user, user=target_user).check_permission(
            UserPermissions.Permissions.CAN_MANAGE_USER_TOKENS)

    def _get(self, user_id, current_user, current_job):
        """Return tokens for user"""
        user = User.get_by_api_id(user_id)
        if not user_id:
            return {}, 404
        return {
            "data": [
                github_app_oauth_token.get_api_details()
                for github_app_oauth_token in GithubAppOauthToken.get_by_user(user)
            ]
        }


class ApiTerraformUserDetails(AuthenticatedEndpoint):
    """Interface to obtain user details"""

    def check_permissions_get(self, user_id, current_user, current_job):
        """Check permissions"""
        user = User.get_by_api_id(user_id)
        if not user:
            return False
        # @TODO check if users are part of a common organisation
        return True

    def _get(self, user_id, current_user, current_job):
        """Obtain user details"""
        user = User.get_by_api_id(user_id)
        if not user:
            return {}, 404
        return {"data": user.get_api_details(effective_user=current_user)}


class ApiTerraformWellKnown(Resource):

    def get(self):
        """Return terraform well-known config"""
        return {
            'state.v2': '/api/v2/',
            'tfe.v2': '/api/v2/',
            'tfe.v2.1': '/api/v2/',
            'tfe.v2.2': '/api/v2/',
            'motd.v1': '/api/terraform/motd'
        }


class ApiTerraformPing(Resource):

    def get(self):
        """Return empty ping response"""

        # Create empty response with 204 status
        response = make_response({}, 204)
        response.headers['Content-Type'] = 'application/vnd.api+json'
        response.headers['tfp-api-version'] = '2.5'
        response.headers['x-ratelimit-limit'] = '30'
        response.headers['x-ratelimit-remaining'] = '30'
        response.headers['x-ratelimit-reset'] = '1'
        return response


class ApiTerraformAccountDetails(AuthenticatedEndpoint):
    """Interface to obtain current account"""

    def check_permissions_get(self, current_user, current_job):
        """Check permissions to access account details."""
        # All users can view their own account details
        return True

    def _get(self, current_user, current_job):
        """Get current account details"""
        return {'data': current_user.get_account_details(current_user)}


class ApiTerraformMotd(Resource):
    """Return MOTD for terraform"""

    def get(self):
        """Return MOTD message."""
        return {
            'msg': 'This is a test Terrarun server\nNo functionality yet.'
        }


class ApiTerraformOrganisation(AuthenticatedEndpoint):
    """Interface for listing/creating organisations"""

    def check_permissions_get(self, *args, **kwargs):
        """Check permissions for endpoint."""
        # Since organisations are obtained based on user permissions for organisation,
        # do not do any permission checking
        return True

    def _get(self, current_user, current_job):
        """Obtain list of organisations"""
        views = [
            OrganizationView.from_object(organisation, effective_user=current_user)
            for organisation in current_user.organisations
        ]
        return ListView(views=views).to_response()

    def check_permissions_post(self, current_user, current_job):
        """Check permissions"""
        return UserPermissions(current_user=current_user, user=current_user).check_permission(
            UserPermissions.Permissions.CAN_CREATE_ORGANISATIONS)

    def _post(self, current_user, current_job):
        """Create new organisation"""
        err, create_entity = OrganizationCreateEntity.from_request(request.json)
        if err:
            return ApiErrorView(error=err).to_response()

        try:
            organisation = Organisation.create(**create_entity.get_set_object_attributes())
        except ApiError as exc:
            return ApiErrorView(error=exc).to_response()

        view = OrganizationView.from_object(organisation, effective_user=current_user)
        return view.to_response()


class ApiTerraformOrganisationDetails(AuthenticatedEndpoint):
    """Organisation details endpoint"""

    def check_permissions_get(self, organisation_name, current_user, current_job, *args, **kwargs):
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return False
        return OrganisationPermissions(organisation=organisation, current_user=current_user).check_permission(
            OrganisationPermissions.Permissions.CAN_ACCESS_VIA_TEAMS)

    def _get(self, current_user, current_job, organisation_name):
        """Get organisation details"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return {}, 404

        view = OrganizationView.from_object(organisation, effective_user=current_user)
        return view.to_response()

    def check_permissions_patch(self, organisation_name, current_user, current_job, *args, **kwargs):
        """Check permissions for updating organsation"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return False
        return OrganisationPermissions(organisation=organisation, current_user=current_user).check_permission(
            OrganisationPermissions.Permissions.CAN_UPDATE)

    def _patch(self, current_user, current_job, organisation_name):
        """Get organisation details"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return {}, 404

        err, update_entity = OrganizationUpdateEntity.from_request(request.json)
        if err:
            return ApiErrorView(error=err).to_response()

        try:
            organisation.update_from_entity(update_entity)
        except ApiError as exc:
            return ApiErrorView(error=exc).to_response()

        view = OrganizationView.from_object(organisation, effective_user=current_user)
        return view.to_response()


class ApiTerraformOrganisationEntitlementSet(AuthenticatedEndpoint):
    """Organisation entitlement endpoint."""

    def check_permissions_get(self, organisation_name, current_user, current_job, *args, **kwargs):
        """Check permissions"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return False

        # Allow job access, if the organisation matches
        if current_job and current_job.run.configuration_version.workspace.organisation == organisation:
            return True

        return OrganisationPermissions(organisation=organisation, current_user=current_user).check_permission(
            OrganisationPermissions.Permissions.CAN_ACCESS_VIA_TEAMS)

    def _get(self, current_user, current_job, organisation_name):
        """Return entitlement-set for organisation"""
        organisation = Organisation.get_by_name_id(organisation_name)
        return organisation.get_entitlement_set_api()


class ApiTerraformOrganisationWorkspaces(AuthenticatedEndpoint):
    """Interface to list/create organisation workspaces"""

    def check_permissions_get(self, organisation_name, current_user, current_job, *args, **kwargs):
        """Check permissions"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return False
        return OrganisationPermissions(organisation=organisation, current_user=current_user).check_permission(
            OrganisationPermissions.Permissions.CAN_ACCESS_VIA_TEAMS)

    def _get(self, organisation_name, current_user, current_job):
        """Return list of workspaces for organisation"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return {}, 404

        # Obtain project names from search_tags
        project_search = request.args.get('search[tags]', None)
        if project_search:
            workspaces = []
            # Iterate over projects and, if they exist, add their
            # environments to the list of environments to return
            for project_name in project_search.split(','):
                if project_name:
                    project = Project.get_by_name(organisation=organisation, name=project_name)
                    if project is not None:
                        workspaces += project.workspaces

            # Return 404 if no workspaces were found
            if not workspaces:
                return {}, 404

        # If no search tags are provided, return all workspaces
        else:
            workspaces = organisation.workspaces

        return {
            "data": [
                workspace.get_api_details(effective_user=current_user)[0]
                for workspace in workspaces
            ]
        }

    def check_permissions_post(self, organisation_name, current_user, current_job, *args, **kwargs):
        """Check permissions"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            logger.error('Organisation "%s" not found.', organisation_name)
            return False
        return OrganisationPermissions(organisation=organisation, current_user=current_user).check_permission(
            OrganisationPermissions.Permissions.CAN_CREATE_WORKSPACE)

    def _post(self, organisation_name, current_user, current_job):
        """Return list of workspaces for organisation"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return {}, 404

        json_data = flask.request.get_json().get('data', {})
        if json_data.get('type') != "workspaces":
            return {}, 400

        attributes = json_data.get('attributes', {})
        name = attributes.get('name')
        if not name:
            return {}, 400

        workspace = Workspace.create(organisation=organisation, name=name)

        return {
            "data": workspace.get_api_details(effective_user=current_user)[0]
        }


class ApiTerraformOrganisationTasks(AuthenticatedEndpoint):
    """Interface to interact with organisation tasks."""

    def check_permissions_get(self, organisation_name, current_user, current_job, *args, **kwargs):
        """Check permissions"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return False
        return OrganisationPermissions(organisation=organisation, current_user=current_user).check_permission(
            OrganisationPermissions.Permissions.CAN_ACCESS_VIA_TEAMS)

    def _get(self, organisation_name, current_user, current_job):
        """Return list of tasks for organisation"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return {}, 404

        return {
            "data": [
                task.get_api_details()
                for task in organisation.tasks
            ]
        }

    def check_permissions_post(self, organisation_name, current_user, current_job, *args, **kwargs):
        """Check permissions"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            logger.error('Organization "%s" not found.', organisation_name)
            return False
        return OrganisationPermissions(organisation=organisation, current_user=current_user).check_permission(
            OrganisationPermissions.Permissions.CAN_MANAGE_RUN_TASKS)

    def _post(self, organisation_name, current_user, current_job):
        """Create organisation task"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return {}, 404

        json_data = flask.request.get_json().get('data', {})
        if json_data.get('type') != "tasks":
            return {}, 400

        attributes = json_data.get('attributes', {})
        task = Task.create(
            organisation=organisation,
            name=attributes.get('name'),
            description=attributes.get('description'),
            enabled=attributes.get('enabled'),
            hmac_key=attributes.get('hmac-key'),
            url=attributes.get('url')
        )

        return {
            "data": task.get_api_details()
        }


class ApiTerraformOrganisationEnvironments(AuthenticatedEndpoint):
    """Interface to list/create organisation environments"""

    def check_permissions_get(self, organisation_name, current_user, current_job, *args, **kwargs):
        """Check permissions"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return False
        return OrganisationPermissions(organisation=organisation, current_user=current_user).check_permission(
            # Most admin permission
            OrganisationPermissions.Permissions.CAN_ACCESS_VIA_TEAMS)

    def _get(self, organisation_name, current_user, current_job):
        """Return list of environments for organisation"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return {}, 404

        return {
            "data": [
                environment.get_api_details()
                for environment in organisation.environments
            ]
        }

    def check_permissions_post(self, organisation_name, current_user, current_job, *args, **kwargs):
        """Check permissions"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return False
        return OrganisationPermissions(organisation=organisation, current_user=current_user).check_permission(
            OrganisationPermissions.Permissions.CAN_DESTROY)

    def _post(self, organisation_name, current_user, current_job):
        """Create environment"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return {}, 404

        json_data = flask.request.get_json().get('data', {})
        if json_data.get('type') != "environments":
            return {}, 400

        attributes = json_data.get('attributes', {})
        name = attributes.get('name')
        if not name:
            return {}, 400
        description = attributes.get('description')

        environment = Environment.create(
            organisation=organisation,
            name=name,
            description=description
        )

        return {
            "data": environment.get_api_details()
        }


class ApiTerraformEnvironment(AuthenticatedEndpoint):
    """Interface to show/update environment"""

    def check_permissions_get(self, environment_id, current_user, current_job, *args, **kwargs):
        """Check permissions"""
        environment = Environment.get_by_api_id(environment_id)
        if not environment:
            return False
        return OrganisationPermissions(organisation=environment.organisation, current_user=current_user).check_permission(
            OrganisationPermissions.Permissions.CAN_ACCESS_VIA_TEAMS)

    def _get(self, environment_id, current_user, current_job):
        """Return list of environments for organisation"""
        environment = Environment.get_by_api_id(environment_id)
        if not environment:
            return {}, 404

        return {
            "data": environment.get_api_details()
        }

    def check_permissions_patch(self, environment_id, current_user, current_job, *args, **kwargs):
        """Check permissions"""
        environment = Environment.get_by_api_id(environment_id)
        if not environment:
            return False
        return OrganisationPermissions(organisation=environment.organisation, current_user=current_user).check_permission(
            # Most admin permission
            OrganisationPermissions.Permissions.CAN_DESTROY)

    def _patch(self, environment_id, current_user, current_job):
        """Update environment attributes"""
        environment = Environment.get_by_api_id(environment_id)
        if not environment:
            return {}, 404

        json_data = flask.request.get_json().get('data', {})
        if json_data.get('type') != "environments":
            return {}, 400

        attributes = json_data.get('attributes', {})

        update_kwargs = {}
        if 'name' in attributes:
            update_kwargs['name'] = attributes.get('name')
        if 'description' in attributes:
            update_kwargs['description'] = attributes.get('description')

        environment.update_attributes(
            **update_kwargs
        )

        return {
            "data": environment.get_api_details()
        }


class ApiTerraformOrganisationProjects(AuthenticatedEndpoint):
    """Interface to list/create organisation projects"""

    def check_permissions_get(self, organisation_name, current_user, current_job, *args, project_name=None, **kwargs):
        """Check permissions"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return False

        if project_name:
            project = Project.get_by_name(organisation=organisation, name=project_name)
            if not project:
                return False

        return OrganisationPermissions(organisation=organisation, current_user=current_user).check_permission(
            # Most admin permission
            OrganisationPermissions.Permissions.CAN_ACCESS_VIA_TEAMS)

    def _get(self, organisation_name, current_user, current_job, project_name=None):
        """Return list of projects for organisation"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return {}, 404

        # If project has been defined in URL,
        # return just the details for this project
        if project_name:
            if project := Project.get_by_name(organisation=organisation, name=project_name):
                return {
                    "data": project.get_api_details()
                }
            # Meta-workspace doesn't exist
            else:
                return {}, 404

        return {
            "data": [
                project.get_api_details()
                for project in organisation.projects
            ]
        }

    def check_permissions_post(self, organisation_name, current_user, current_job, *args, project_name=None, **kwargs):
        """Check permissions"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return False
        return OrganisationPermissions(organisation=organisation, current_user=current_user).check_permission(
            OrganisationPermissions.Permissions.CAN_CREATE_WORKSPACE)

    def _post(self, organisation_name, current_user, current_job, project_name=None):
        """Create project"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return {}, 404

        if project_name:
            # Meta-workspace cannot be defined in URL for a POST
            return {}, 400

        json_data = flask.request.get_json().get('data', {})
        if json_data.get('type') != "projects":
            return {}, 400

        attributes = json_data.get('attributes', {})
        name = attributes.get('name')
        lifecycle_id = attributes.get('lifecycle')
        lifecycle = Lifecycle.get_by_api_id(lifecycle_id)
        if not name or not lifecycle:
            return {}, 400

        project = Project.create(
            organisation=organisation,
            name=name,
            description=attributes.get('description'),
            lifecycle=lifecycle
        )

        # If meta workspace failed to be cr
        if not project:
            return {}, 400

        return {
            "data": project.get_api_details()
        }


class ApiTerrarunProjectIngressAttributes(AuthenticatedEndpoint):
    """Interface to view ingress attributes for a given project"""

    def check_permissions_get(self, project_id, current_user, current_job, *args, **kwargs):
        """Check permissions"""
        project = Project.get_by_api_id(project_id)
        if not project:
            return False
        return OrganisationPermissions(organisation=project.organisation, current_user=current_user).check_permission(
            OrganisationPermissions.Permissions.CAN_ACCESS_VIA_TEAMS)

    def _get(self, project_id, current_user, current_job):
        """Return list of environments for organisation"""
        project = Project.get_by_api_id(project_id)
        if not project:
            return {}, 404

        api_request = ApiRequest(request, list_data=True)

        # Obtain ingress attributes 
        ingress_attributes = project.get_ingress_attributes(api_request)

        for ingress_attribute in ingress_attributes:
            api_request.set_data(ingress_attribute.get_api_details())

        return api_request.get_response()


class ApiTerraformProject(AuthenticatedEndpoint):
    """Interface to show/update projects"""

    def check_permissions_get(self, project_id, current_user, current_job, *args, **kwargs):
        """Check permissions"""
        project = Project.get_by_api_id(project_id)
        if not project:
            return False
        return OrganisationPermissions(organisation=project.organisation, current_user=current_user).check_permission(
            OrganisationPermissions.Permissions.CAN_ACCESS_VIA_TEAMS)

    def _get(self, project_id, current_user, current_job):
        """Return list of environments for organisation"""
        project = Project.get_by_api_id(project_id)
        if not project:
            return {}, 404

        return {
            "data": project.get_api_details()
        }

    def check_permissions_patch(self, project_id, current_user, current_job, *args, **kwargs):
        """Check permissions"""
        project = Project.get_by_api_id(project_id)
        if not project:
            return False
        return OrganisationPermissions(organisation=project.organisation, current_user=current_user).check_permission(
            # Most admin permission
            OrganisationPermissions.Permissions.CAN_DESTROY)

    def _patch(self, project_id, current_user, current_job):
        """Update attributes of project"""
        project = Project.get_by_api_id(project_id)
        if not project:
            return {}, 404

        json_data = flask.request.get_json().get('data', {})
        if json_data.get('type') != "projects":
            return {}, 400

        attributes = json_data.get('attributes', {})

        errors = project.update_attributes_from_request(attributes)

        if errors:
            return {
                "errors": [
                    error.get_api_details()
                    for error in errors
                ]
            }, 422

        return {
            "data": project.get_api_details()
        }


class ApiTerraformOrganisationLifecycles(AuthenticatedEndpoint):
    """Interface to list/create organisation lifecycles"""

    def check_permissions_get(self, organisation_name, current_user, current_job, *args, **kwargs):
        """Check permissions"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return False
        return OrganisationPermissions(organisation=organisation, current_user=current_user).check_permission(
            OrganisationPermissions.Permissions.CAN_ACCESS_VIA_TEAMS)

    def _get(self, organisation_name, current_user, current_job):
        """Return list of projects for organisation"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return {}, 404

        return {
            "data": [
                lifecycle.get_api_details()
                for lifecycle in organisation.lifecycles
            ]
        }

    def check_permissions_post(self, organisation_name, current_user, current_job, *args, **kwargs):
        """Check permissions"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return False
        return OrganisationPermissions(organisation=organisation, current_user=current_user).check_permission(
            OrganisationPermissions.Permissions.CAN_DESTROY)

    def _post(self, organisation_name, current_user, current_job):
        """Create project"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return {}, 404

        json_data = flask.request.get_json().get('data', {})
        if json_data.get('type') != "lifecycles":
            return {}, 400

        attributes = json_data.get('attributes', {})
        name = attributes.get('name')
        if not name:
            return {}, 400

        environment = Lifecycle.create(organisation=organisation, name=name)

        return {
            "data": environment.get_api_details()
        }


class ApiTerraformEnvironmentLifecycleEnvironments(AuthenticatedEndpoint):
    """Interface to obntain environment lifecycle environments"""

    def check_permissions_get(self, environment_id, current_user, current_job, *args, **kwargs):
        """Check permissions"""
        environment = Environment.get_by_api_id(environment_id)
        if not environment:
            return False
        return OrganisationPermissions(organisation=environment.organisation, current_user=current_user).check_permission(
            OrganisationPermissions.Permissions.CAN_ACCESS_VIA_TEAMS)

    def _get(self, environment_id, current_user, current_job):
        """Return list of projects for organisation"""
        environment = Environment.get_by_api_id(environment_id)
        if not environment:
            return {}, 404

        return {
            "data": [
                lifecycle_environment.get_api_details()
                for lifecycle_environment in environment.lifecycle_environments
            ]
        }


class ApiTerraformLifecycleLifecycleEnvironmentGroups(AuthenticatedEndpoint):
    """Interface to list/create organisation lifecycle environments"""

    def check_permissions_get(self, lifecycle_id, current_user, current_job, *args, **kwargs):
        """Check permissions"""
        lifecycle = Lifecycle.get_by_api_id(lifecycle_id)
        if not lifecycle:
            return False
        return OrganisationPermissions(organisation=lifecycle.organisation, current_user=current_user).check_permission(
            OrganisationPermissions.Permissions.CAN_ACCESS_VIA_TEAMS)

    def _get(self, lifecycle_id, current_user, current_job):
        """Return list of projects for organisation"""
        lifecycle = Lifecycle.get_by_api_id(lifecycle_id)
        if not lifecycle:
            return {}, 404

        return {
            "data": [
                lifecycle_environment_group.get_api_details()
                for lifecycle_environment_group in lifecycle.lifecycle_environment_groups
            ]
        }

    def check_permissions_post(self, lifecycle_id, current_user, current_job, *args, **kwargs):
        """Check permissions"""
        lifecycle = Lifecycle.get_by_api_id(lifecycle_id)
        if not lifecycle:
            return False
        return OrganisationPermissions(organisation=lifecycle.organisation, current_user=current_user).check_permission(
            OrganisationPermissions.Permissions.CAN_MANAGE_ENVIRONMENTS)

    def _post(self, lifecycle_id, current_user, current_job):
        """Create lifecycle environment group"""
        lifecycle = Lifecycle.get_by_api_id(lifecycle_id)
        if not lifecycle:
            return {}, 404

        lifecycle_environment_group = LifecycleEnvironmentGroup.create(lifecycle=lifecycle)

        return {
            "data": lifecycle_environment_group.get_api_details()
        }


class ApiTerraformLifecycleEnvironmentGroup(AuthenticatedEndpoint):
    """Provide interface to obtain details for lifecycle environment group"""

    def check_permissions_get(self, lifecycle_environment_group_id, current_user, current_job, *args, **kwargs):
        """Check permissions"""
        lifecycle_environment_group = LifecycleEnvironmentGroup.get_by_api_id(lifecycle_environment_group_id)
        if not lifecycle_environment_group:
            return False
        return OrganisationPermissions(
            organisation=lifecycle_environment_group.lifecycle.organisation,
            current_user=current_user
        ).check_permission(
            OrganisationPermissions.Permissions.CAN_ACCESS_VIA_TEAMS
        )

    def _get(self, lifecycle_environment_group_id, current_user, current_job):
        """Return lifecycle environment group details"""
        lifecycle_environment_group = LifecycleEnvironmentGroup.get_by_api_id(lifecycle_environment_group_id)
        if not lifecycle_environment_group:
            return {}, 404

        return {
            "data": lifecycle_environment_group.get_api_details()
        }

    def check_permissions_patch(self, lifecycle_environment_group_id, current_user, current_job, *args, **kwargs):
        """Check permissions"""
        lifecycle_environment_group = LifecycleEnvironmentGroup.get_by_api_id(lifecycle_environment_group_id)
        if not lifecycle_environment_group:
            return False
        return OrganisationPermissions(
            organisation=lifecycle_environment_group.lifecycle.organisation,
            current_user=current_user
        ).check_permission(
            OrganisationPermissions.Permissions.CAN_MANAGE_ENVIRONMENTS
        )

    def _patch(self, lifecycle_environment_group_id, current_user, current_job):
        """Update lifecycle environment group details"""
        lifecycle_environment_group = LifecycleEnvironmentGroup.get_by_api_id(lifecycle_environment_group_id)
        if not lifecycle_environment_group:
            return {}, 404

        data = request.json.get("data", {})

        if data.get("type") != "lifecycle-environment-groups":
            return {}, 400

        if data.get("id") != lifecycle_environment_group_id:
            return {}, 400

        request_attributes = data.get("attributes", {})

        update_attributes = {
            target_attribute: request_attributes.get(req_attribute)
            for req_attribute, target_attribute in {
                "minimum-runs": "minimum_runs", "minimum-successful-plans": "minimum_successful_plans",
                "minimum-successful-applies": "minimum_successful_applies"
            }.items()
            if req_attribute in request_attributes
        }

        lifecycle_environment_group.update_attributes(
            **update_attributes
        )

        return {
            "data": lifecycle_environment_group.get_api_details()
        }

    def check_permissions_delete(self, lifecycle_environment_group_id, current_user, current_job, *args, **kwargs):
        """Check permissions"""
        lifecycle_environment_group = LifecycleEnvironmentGroup.get_by_api_id(lifecycle_environment_group_id)
        if not lifecycle_environment_group:
            return False
        return OrganisationPermissions(
            organisation=lifecycle_environment_group.lifecycle.organisation,
            current_user=current_user
        ).check_permission(
            OrganisationPermissions.Permissions.CAN_MANAGE_ENVIRONMENTS
        )

    def _delete(self, lifecycle_environment_group_id, current_user, current_job):
        """Delete lifecycle environment group"""
        lifecycle_environment_group = LifecycleEnvironmentGroup.get_by_api_id(lifecycle_environment_group_id)
        if not lifecycle_environment_group:
            return {}, 404

        if lifecycle_environment_group.lifecycle_environments:
            return {
                "errors": [ApiError(
                    "Lifecycle environment group has environments assigned",
                    "The lifecycle environment group cannot be deleted whilst it has environments assigned to it"
                ).get_api_details()]
            }, 422

        lifecycle_environment_group.delete()

        return {}, 200


class ApiTerraformLifecycleEnvironment(AuthenticatedEndpoint):
    """Interface to view/delete lifecycle environments"""

    def check_permissions_get(self, lifecycle_environment_id, current_user, current_job, *args, **kwargs):
        """Check permissions"""
        lifecycle_environment = LifecycleEnvironment.get_by_api_id(lifecycle_environment_id)
        if not lifecycle_environment:
            return False
        return OrganisationPermissions(
            organisation=lifecycle_environment.lifecycle_environment_group.lifecycle.organisation,
            current_user=current_user
        ).check_permission(
            OrganisationPermissions.Permissions.CAN_ACCESS_VIA_TEAMS
        )

    def _get(self, lifecycle_environment_id, current_user, current_job):
        """Return lifecycle environment details"""
        lifecycle_environment = LifecycleEnvironment.get_by_api_id(lifecycle_environment_id)
        if not lifecycle_environment:
            return {}, 404

        return {
            "data": lifecycle_environment.get_api_details()
        }

    def check_permissions_delete(self, lifecycle_environment_id, current_user, current_job, *args, **kwargs):
        """Check permissions"""
        lifecycle_environment = LifecycleEnvironment.get_by_api_id(lifecycle_environment_id)
        if not lifecycle_environment:
            return False
        return OrganisationPermissions(
            organisation=lifecycle_environment.lifecycle_environment_group.lifecycle.organisation,
            current_user=current_user
        ).check_permission(
            OrganisationPermissions.Permissions.CAN_MANAGE_ENVIRONMENTS
        )

    def _delete(self, lifecycle_environment_id, current_user, current_job):
        """Delete lifecycle environment"""
        lifecycle_environment = LifecycleEnvironment.get_by_api_id(lifecycle_environment_id)
        if not lifecycle_environment:
            return {}, 404

        lifecycle_environment.delete()

        return {}, 200


class ApiTerraformLifecycleEnvironmentGroupLifecycleEnvironments(AuthenticatedEndpoint):
    """Interface to obtain list of lifecycle group's lifecycle enivronments"""

    def check_permissions_get(self, lifecycle_environment_group_id, current_user, current_job, *args, **kwargs):
        """Check permissions"""
        lifecycle_environment_group = LifecycleEnvironmentGroup.get_by_api_id(lifecycle_environment_group_id)
        if not lifecycle_environment_group:
            return False
        return OrganisationPermissions(
            organisation=lifecycle_environment_group.lifecycle.organisation,
            current_user=current_user
        ).check_permission(
            OrganisationPermissions.Permissions.CAN_ACCESS_VIA_TEAMS
        )

    def _get(self, lifecycle_environment_group_id, current_user, current_job):
        """Return lifecycle environment group details"""
        lifecycle_environment_group = LifecycleEnvironmentGroup.get_by_api_id(lifecycle_environment_group_id)
        if not lifecycle_environment_group:
            return {}, 404

        return {
            "data": [
                lifecycle_environment.get_api_details()
                for lifecycle_environment in lifecycle_environment_group.lifecycle_environments
            ]
        }

    def check_permissions_post(self, lifecycle_environment_group_id, current_user, current_job, *args, **kwargs):
        """Check permissions"""
        lifecycle_environment_group = LifecycleEnvironmentGroup.get_by_api_id(lifecycle_environment_group_id)
        if not lifecycle_environment_group:
            return False
        return OrganisationPermissions(
            organisation=lifecycle_environment_group.lifecycle.organisation,
            current_user=current_user
        ).check_permission(
            OrganisationPermissions.Permissions.CAN_MANAGE_ENVIRONMENTS
        )

    def _post(self, lifecycle_environment_group_id, current_user, current_job):
        """Create lifecycle environment"""
        lifecycle_environment_group = LifecycleEnvironmentGroup.get_by_api_id(lifecycle_environment_group_id)
        if not lifecycle_environment_group:
            return {}, 404

        data = request.json.get("data", {})

        if data.get("type") != "lifecycle-environments":
            return {}, 400

        if data.get("id"):
            return {}, 400

        environment_details = data.get("relationships", {}).get("environment", {}).get("data")
        if not environment_details:
            return api_error_response(ApiError("Missing environment relationship", pointer="/data/relationships/environment/data"))
        if environment_details.get("type") != "environments":
            return api_error_response(ApiError("Invalid environment relationship type", pointer="/data/relationships/environment/data/type"))

        environment = Environment.get_by_api_id(environment_details.get("id"))

        if environment is None or environment.organisation != lifecycle_environment_group.lifecycle.organisation:
            return api_error_response(ApiError("Environment does not exist", pointer="/data/relationships/environment/data/id"))

        lifecycle_environment = LifecycleEnvironment.create(
            lifecycle_environment_group=lifecycle_environment_group,
            environment=environment
        )

        return {
            "data": lifecycle_environment.get_api_details()
        }


class ApiTerraformOrganisationLifecycle(AuthenticatedEndpoint):
    """Interface to show/update lifecycles"""

    def check_permissions_get(self, organisation_name, lifecycle_name, current_user, current_job, *args, **kwargs):
        """Check permissions"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return False

        lifecycle = Lifecycle.get_by_name_and_organisation(name=lifecycle_name, organisation=organisation)
        if not lifecycle:
            return False

        return OrganisationPermissions(organisation=organisation, current_user=current_user).check_permission(
            OrganisationPermissions.Permissions.CAN_ACCESS_VIA_TEAMS)

    def _get(self, organisation_name, lifecycle_name, current_user, current_job):
        """Return list of projects for organisation"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return {}, 404

        lifecycle = Lifecycle.get_by_name_and_organisation(name=lifecycle_name, organisation=organisation)
        if not lifecycle:
            return {}, 404

        return {
            "data": lifecycle.get_api_details()
        }


class ApiTerraformLifecycle(AuthenticatedEndpoint):
    """Interface to show/update lifecycles"""

    def check_permissions_get(self, lifecycle_id, current_user, current_job, *args, **kwargs):
        """Check permissions"""
        lifecycle = Lifecycle.get_by_api_id(lifecycle_id)
        if not lifecycle:
            return False
        return OrganisationPermissions(organisation=lifecycle.organisation, current_user=current_user).check_permission(
            OrganisationPermissions.Permissions.CAN_ACCESS_VIA_TEAMS)

    def _get(self, lifecycle_id, current_user, current_job):
        """Return list of environments for organisation"""
        lifecycle = Lifecycle.get_by_api_id(lifecycle_id)
        if not lifecycle:
            return {}, 404

        return {
            "data": lifecycle.get_api_details()
        }

    def check_permissions_patch(self, lifecycle_id, current_user, current_job, *args, **kwargs):
        """Check permissions"""
        lifecycle = Lifecycle.get_by_api_id(lifecycle_id)
        if not lifecycle:
            return False
        return OrganisationPermissions(organisation=lifecycle.organisation, current_user=current_user).check_permission(
            # Most admin permission
            OrganisationPermissions.Permissions.CAN_MANAGE_ENVIRONMENTS)

    def _patch(self, lifecycle_id, current_user, current_job):
        """Update lifecycle"""
        lifecycle = Lifecycle.get_by_api_id(lifecycle_id)
        if not lifecycle:
            return {}, 404

        json_data = flask.request.get_json().get('data', {})
        if json_data.get('type') != "lifecycles":
            return {}, 400

        if json_data.get('id') != lifecycle_id:
            return {}, 400

        request_attributes = json_data.get('attributes', {})

        update_attributes = {
            target_attribute: request_attributes.get(req_attribute)
            for req_attribute, target_attribute in {
                "name": "name", "description": "description",
                "allow-per-workspace-vcs": "allow_per_workspace_vcs"
            }.items()
            if req_attribute in request_attributes
        }        

        lifecycle.update_attributes(
            **update_attributes
        )

        return {
            "data": lifecycle.get_api_details()
        }


class ApiTerraformTaskDetails(AuthenticatedEndpoint):
    """Interface to view/edit a task"""

    def check_permissions_patch(self, task_id, current_user, current_job):
        """Check permissions"""
        task = Task.get_by_api_id(task_id)
        if not task:
            return False
        return OrganisationPermissions(
                organisation=task.organisation,
                current_user=current_user).check_permission(
            OrganisationPermissions.Permissions.CAN_MANAGE_RUN_TASKS)

    def _patch(self, task_id, current_user, current_job):
        """Update task details"""
        task = Task.get_by_api_id(task_id)

        json_data = flask.request.get_json().get('data', {})
        if json_data.get('type') != "tasks":
            return {}, 400

        attributes = json_data.get('attributes', {})

        task.update_attributes(
            name=attributes.get('name'),
            description=attributes.get('description'),
            enabled=attributes.get('enabled'),
            hmac_key=attributes.get('hmac-key'),
            url=attributes.get('url')
        )


class ApiTerraformWorkspace(AuthenticatedEndpoint):
    """Organisation workspace details endpoint."""

    def _get_workspace(self, organisation_name, workspace_name, workspace_id):
        """Obtain workspace given either workspace ID or organisation/workspace names"""
        # Handle URLs containing organisation and workspace name
        if organisation_name and workspace_name:
            organisation = Organisation.get_by_name_id(organisation_name)
            if not organisation:
                return None

            return Workspace.get_by_organisation_and_name(organisation, workspace_name)
        # Handle URLs containing workspace ID
        elif workspace_id:
            return Workspace.get_by_api_id(workspace_id)
        return None

    def check_permissions_get(self, current_user, current_job,
                              organisation_name=None, workspace_name=None, workspace_id=None,
                              *args, **kwargs):
        """Check permissions"""
        workspace = self._get_workspace(
            organisation_name=organisation_name,
            workspace_name=workspace_name,
            workspace_id=workspace_id
        )
        if not workspace:
            return False

        if current_job and current_job.run.configuration_version.workspace == workspace:
            return True

        return WorkspacePermissions(current_user=current_user, workspace=workspace).check_permission(
            WorkspacePermissions.Permissions.CAN_READ_SETTINGS)

    def _get(self, current_user, current_job,
             organisation_name=None, workspace_name=None, workspace_id=None):
        """Return workspace details."""
        workspace = self._get_workspace(
            organisation_name=organisation_name,
            workspace_name=workspace_name,
            workspace_id=workspace_id
        )
        if not workspace:
            return {}, 404

        includes = request.args.get("include", "").split(",")

        data, include_response = workspace.get_api_details(effective_user=current_user, includes=includes)
        api_response = {"data": data}
        if includes is not None:
            api_response["included"] = include_response
        return api_response


    def check_permissions_patch(self, current_user, current_job,
                                organisation_name=None, workspace_name=None, workspace_id=None):
        """Check permissions for updating workspace"""
        workspace = self._get_workspace(
            organisation_name=organisation_name,
            workspace_name=workspace_name,
            workspace_id=workspace_id
        )
        if not workspace:
            return False

        return WorkspacePermissions(current_user=current_user, workspace=workspace).check_permission(
            WorkspacePermissions.Permissions.CAN_UPDATE)

    def _patch(self, current_user, current_job,
               organisation_name=None, workspace_name=None, workspace_id=None):
        """Update workspace"""
        workspace = self._get_workspace(
            organisation_name=organisation_name,
            workspace_name=workspace_name,
            workspace_id=workspace_id
        )
        if not workspace:
            return {}, 404

        json_data = flask.request.get_json().get('data', {})
        if json_data.get('type') != "workspaces":
            return {}, 400

        attributes = json_data.get('attributes', {})

        errors = workspace.update_attributes_from_request(
            attributes
        )
        if errors:
            return {
                "errors": [
                    error.get_api_details()
                    for error in errors
                ]
            }, 422
        return {"data": workspace.get_api_details(effective_user=current_user)[0]}


class ApiTerraformWorkspaceConfigurationVersions(AuthenticatedEndpoint):
    """Workspace configuration version interface"""

    def check_permissions_get(self, current_user, current_job, workspace_id):
        """Check permissions"""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return False

        return WorkspacePermissions(
            current_user=current_user,
            workspace=workspace
        ).check_access_type(runs=TeamWorkspaceRunsPermission.READ)

    def _get(self, workspace_id, current_user, current_job):
        """Return configuration versions for a workspace."""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return {}, 404

        api_request = ApiRequest(
            request,
            list_data=True,
            query_map={
                "filter[commit]": IngressAttribute.commit_sha
            }
        )

        for configuration_version in workspace.get_configuration_versions(api_request):
            api_request.set_data(configuration_version.get_api_details(api_request))

        return api_request.get_response()

    def check_permissions_post(self, workspace_id, current_user, current_job, *args, **kwargs):
        """Check permissions"""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return False

        # As per documentation:
        # You need read runs permission to list and view configuration versions for a workspace, and you need queue plans permission to create new configuration versions.
        return WorkspacePermissions(current_user=current_user,
                                    workspace=workspace).check_access_type(
                                        runs=TeamWorkspaceRunsPermission.PLAN)

    def _post(self, workspace_id, current_user, current_job):
        """Create configuration version"""
        data = flask.request.get_json().get('data', {})
        attributes = data.get('attributes', {})

        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return {}, 404

        api_request = ApiRequest(request)
        cv = ConfigurationVersion.create(
            workspace=workspace,
            auto_queue_runs=attributes.get('auto-queue-runs', True),
            speculative=attributes.get('speculative', False)
        )
        api_request.set_data(cv.get_api_details())

        return api_request.get_response()


class ApiTerraformWorkspaceRelationshipsTags(AuthenticatedEndpoint):
    """Interface to manage workspace tags"""

    def check_permissions_post(self, workspace_id, current_user, current_job):
        workspace = Workspace.get_by_api_id(workspace_id)
        if workspace is None:
            return False
        return WorkspacePermissions(
            current_user=current_user, workspace=workspace).check_permission(
            WorkspacePermissions.Permissions.CAN_MANAGE_TAGS)

    def _post(self, current_user, current_job, workspace_id):
        """Handle updating workspace tags"""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return 404

        request_data = request.json
        db = Database.get_session()
        for row in request_data.get('data', []):
            if row.get('type', None) != 'tags':
                return {}, 400
            tag_name = row.get('attributes', None).get('name', None)
            if not tag_name:
                return {}, 400
            tag = Tag.get_by_organisation_and_name(organisation=workspace.organisation, tag_name=tag_name)
            if not tag:
                tag = Tag.create(organisation=workspace.organisation, tag_name=tag_name)
            workspace.add_tag(tag)


class ApiTerraformOrganisationWorkspaceRelationshipsProjects(AuthenticatedEndpoint):
    """Interface to obtain workspace's project"""

    def check_permissions_get(self, organisation_name, workspace_name, current_user, current_job):
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return False
        workspace = Workspace.get_by_organisation_and_name(organisation, workspace_name)
        if not workspace:
            return False
        return WorkspacePermissions(current_user=current_user, workspace=workspace).check_permission(
            WorkspacePermissions.Permissions.CAN_READ_SETTINGS)

    def _get(self, current_user, current_job, organisation_name, workspace_name):
        """Obtain workspace project details"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return False
        workspace = Workspace.get_by_organisation_and_name(organisation, workspace_name)
        if not workspace:
            return False

        return {'data': workspace.project.get_api_details()}


class ApiTerraformConfigurationVersions(AuthenticatedEndpoint):
    """Workspace configuration version interface"""

    def check_permissions_get(self, current_user, current_job, configuration_version_id):
        """Check permissions"""
        cv = ConfigurationVersion.get_by_api_id(configuration_version_id)
        if not cv:
            return False
        return WorkspacePermissions(current_user=current_user,
                                    workspace=cv.workspace).check_access_type(
                                        runs=TeamWorkspaceRunsPermission.READ)

    def _get(self, configuration_version_id, current_user, current_job):
        """Get configuration version details."""
        cv = ConfigurationVersion.get_by_api_id(configuration_version_id)
        if not cv:
            return {}, 404

        api_request = ApiRequest(request)
        api_request.set_data(cv.get_api_details())
        return api_request.get_response()


class ApiTerraformConfigurationVersionUpload(AuthenticatedEndpoint):
    """Configuration version upload endpoint"""

    def check_permissions_put(self, current_user, current_job, configuration_version_id):
        """Check permissions"""
        cv = ConfigurationVersion.get_by_api_id(configuration_version_id)
        if not cv:
            return False
        return WorkspacePermissions(current_user=current_user,
                                    workspace=cv.workspace).check_access_type(
                                        runs=TeamWorkspaceRunsPermission.PLAN)

    def _put(self, configuration_version_id, current_user, current_job):
        """Handle upload of configuration version data."""
        cv = ConfigurationVersion.get_by_api_id(configuration_version_id)
        if not cv:
            return {}, 404

        cv.process_upload(request.data)


class ApiTerraformRunConfigurationVersionDownload(AuthenticatedEndpoint):
    """Interface to download configuration version"""

    def check_permissions_get(self, current_user, current_job, run_id):
        """Check permissions"""
        run = Run.get_by_api_id(run_id)
        if not run:
            return False

        return (WorkspacePermissions(
                current_user=current_user,
                workspace=run.configuration_version.workspace
            ).check_access_type(runs=TeamWorkspaceRunsPermission.READ) or
            current_user.has_task_execution_run_access(run=run)
        )

    def _get(self, current_user, current_job, run_id):
        """Download configuration versinon"""
        run = Run.get_by_api_id(run_id)
        if not run:
            return {}, 404

        response = make_response(run.configuration_version.configuration_blob.data)
        # Considered wheteher to use application/gzip, application/tar
        response.headers['Content-Type'] = 'application/tar+gzip'
        return response


class ApiTerraformRun(AuthenticatedEndpoint):
    """Run interface."""

    def check_permissions_get(self, current_user, current_job, run_id=None,):
        """Check permissions to view run"""
        if not run_id:
            return False
        run = Run.get_by_api_id(run_id)
        if not run:
            return False

        return WorkspacePermissions(
            current_user=current_user,
            workspace=run.configuration_version.workspace
        ).check_access_type(runs=TeamWorkspaceRunsPermission.READ)

    def _get(self, current_user, current_job, run_id=None):
        """Return run information"""
        if not run_id:
            return {}, 404
        run = Run.get_by_api_id(run_id)
        if not run:
            return {}, 404
        return {"data": run.get_api_details()}

    def check_permissions_post(self, current_user, current_job, run_id=None,):
        """Check permissions to view run"""
        if run_id:
            return False

        data = flask.request.get_json().get('data', {})
        workspace_id = data.get('relationships', {}).get('workspace', {}).get('data', {}).get('id', None)
        if not workspace_id:
            return False

        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return False

        return WorkspacePermissions(
            current_user=current_user,
            workspace=workspace
        ).check_access_type(runs=TeamWorkspaceRunsPermission.PLAN)

    def _post(self, current_user, current_job, run_id=None):
        """Create a run."""

        if run_id:
            return {}, 422

        # print("CREATE RUN JSON")
        # print(flask.request.get_json())

        data = flask.request.get_json().get('data', {})
        request_attributes = data.get('attributes', {})

        api_request = ApiRequest(request)

        workspace_id = data.get('relationships', {}).get('workspace', {}).get('data', {}).get('id', None)
        if not workspace_id:
            return {}, 422

        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return {}, 404


        configuration_version_id = data.get('relationships', {}).get('configuration-version', {}).get('data', {}).get('id', None)
        cv = None
        if configuration_version_id:
            cv = ConfigurationVersion.get_by_api_id(configuration_version_id)
            if not cv:
                return {}, 404
        elif workspace.can_run_vcs_build:
            cv = ConfigurationVersion.generate_from_vcs(
                workspace=workspace,
                speculative=request_attributes.get('plan-only', False)
            )
            if not cv:
                return {}, 400
        else:
            logger.error("Cannot run VCS build and no configuration version provided!")
            return {}, 400

        if cv.workspace.id != workspace.id:
            logger.error('Configuration version does not belong to this workspace.')
            # Hide error to prevent workspace ID/configuration ID enumeration
            return {}, 400

        tool = None
        if request_terraform_version := request_attributes.get('terraform-version'):
            tool = Tool.get_by_version(
                tool_type=ToolType.TERRAFORM_VERSION,
                version=request_terraform_version
            )
            if not tool:
                return {
                    "errors": [
                        ApiError(
                            'Invalid tool version',
                            'The tool version is invalid or the tool version does not exist.',
                            pointer='/data/attributes/terraform-version'
                        ).get_api_details()
                    ]
                }, 422

        create_attributes = {
            'auto_apply': request_attributes.get('auto-apply', workspace.auto_apply),
            'is_destroy': request_attributes.get('is-destroy', False),
            'message': request_attributes.get('message', "Queued manually via the Terraform Enterprise API"),
            'refresh': request_attributes.get('refresh', True),
            'refresh_only': request_attributes.get('refresh-only', False),
            'replace_addrs': request_attributes.get('replace-addrs'),
            'target_addrs': request_attributes.get('target-addrs'),
            'variables': request_attributes.get('variables', []),
            'plan_only': cv.plan_only if cv.plan_only else request_attributes.get('plan-only', cv.plan_only),
            'tool': tool,
            'allow_empty_apply': request_attributes.get('allow-empty-apply')
        }

        try:
            run = Run.create(configuration_version=cv, created_by=current_user, **create_attributes)
        except ApiError as exc:
            api_request.add_error(exc)
            return api_request.get_response()

        return {"data": run.get_api_details()}


class ApiTerraformRunRunEvents(AuthenticatedEndpoint):
    """Interface to obtain run events for run"""

    def check_permissions_get(self, current_user, current_job, run_id):
        """Check permissions"""
        run = Run.get_by_api_id(run_id)
        if not workspace:
            return False

        return WorkspacePermissions(
            current_user=current_user,
            workspace=run.configuration_version.workspace.organisation
        ).check_access_type(runs=TeamWorkspaceRunsPermission.READ)

    def _get(self, run_id, current_user, current_job):
        """Return all audit events for run."""
        run = Run.get_by_api_id(run_id)
        if not run:
            return {}, 404

        return {"data": [
            event.get_api_details()
            for event in run.run_events
        ]}


class ApiTerraformRunAuditEvents(AuthenticatedEndpoint):
    """Interface to obtain audit events for run"""

    def check_permissions_get(self, current_user, current_job, run_id):
        """Check permissions"""
        run = Run.get_by_api_id(run_id)
        if not workspace:
            return False

        return WorkspacePermissions(
            current_user=current_user,
            workspace=run.configuration_version.workspace.organisation
        ).check_access_type(runs=TeamWorkspaceRunsPermission.READ)

    def _get(self, run_id, current_user, current_job):
        """Return all audit events for run."""
        run = Run.get_by_api_id(run_id)
        if not run:
            return {}, 404

        events = AuditEvent.get_by_object_type_and_object_id(object_type='run', object_id=run.id)

        return {"data": [
            event.get_api_details()
            for event in events
        ]}


class ApiTerraformRunActionsCancel(AuthenticatedEndpoint):
    """Interface to cancel runs"""

    def check_permissions_post(self, run_id, current_user, current_job):
        run = Run.get_by_api_id(run_id)
        if not run:
            return False
        if run.plan_only:
            return WorkspacePermissions(
                current_user=current_user,
                workspace=run.configuration_version.workspace
            ).check_access_type(runs=TeamWorkspaceRunsPermission.PLAN)
        return WorkspacePermissions(
                current_user=current_user,
                workspace=run.configuration_version.workspace
            ).check_access_type(runs=TeamWorkspaceRunsPermission.APPLY)

    def _post(self, run_id, current_user, current_job):
        """Cancel run"""
        run = Run.get_by_api_id(run_id)
        if not run:
            return {}, 404

        run.cancel(user=current_user)


class ApiTerraformRunActionsDiscard(AuthenticatedEndpoint):
    """Interface to discard runs"""

    def check_permissions_post(self, run_id, current_user, current_job):
        run = Run.get_by_api_id(run_id)
        if not run:
            return False
        return WorkspacePermissions(
            current_user=current_user,
            workspace=run.configuration_version.workspace
        ).check_access_type(runs=TeamWorkspaceRunsPermission.APPLY)

    def _post(self, run_id, current_user, current_job):
        """Cancel run"""
        run = Run.get_by_api_id(run_id)
        if not run:
            return {}, 404

        run.discard(user=current_user)


class ApiTerraformWorkspaceRuns(AuthenticatedEndpoint):
    """Interface to obtain workspace runs,"""

    def check_permissions_get(self, current_user, current_job, workspace_id):
        """Check permissions"""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return False

        return WorkspacePermissions(
            current_user=current_user,
            workspace=workspace
        ).check_access_type(runs=TeamWorkspaceRunsPermission.READ)

    def _get(self, workspace_id, current_user, current_job):
        """Return all runs for a workspace."""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return {}, 404

        api_request = ApiRequest(request, list_data=True)
        
        for run in workspace.runs:
            api_request.set_data(run.get_api_details(api_request))

        return api_request.get_response()

    def check_permissions_post(self, current_user, current_job, workspace_id):
        """Check permissions for run creation"""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return False

        return WorkspacePermissions(
            current_user=current_user,
            workspace=workspace
        ).check_access_type(runs=TeamWorkspaceRunsPermission.PLAN)

    def _post(self, workspace_id, current_user, current_job):
        """Handle run creation"""
        raise Exception("create run was called via workspace/runs")


class ApiTerraformOrganisationQueue(AuthenticatedEndpoint):
    """Interface to obtain run queue for organisation"""

    def check_permissions_get(self, current_user, current_job, organisation_name):
        """Check permissions"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return {}, 404

        # @TODO Check this permission
        return OrganisationPermissions(
            current_user=current_user,
            organisation=organisation
        ).check_permission(OrganisationPermissions.Permissions.CAN_ACCESS_VIA_TEAMS)

    def _get(self, organisation_name, current_user, current_job):
        """Get list of runs queued"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return {}, 404

        return {"data": [run.get_api_details() for run in organisation.get_run_queue()]}


class ApiTerraformOrganisationOauthClients(AuthenticatedEndpoint):
    """Interface to view/create oauth clients"""

    def check_permissions_get(self, current_user, current_job, organisation_name):
        """Check permissions"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return {}, 404

        # @TODO Check this permission
        return OrganisationPermissions(
            current_user=current_user,
            organisation=organisation
        ).check_permission(OrganisationPermissions.Permissions.CAN_ACCESS_VIA_TEAMS)

    def _get(self, organisation_name, current_user, current_job):
        """Get list of runs queued"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return {}, 404

        return {
            "data": [
                oauth_client.get_api_details()
                for oauth_client in organisation.oauth_clients
            ]
        }

    def check_permissions_post(self, current_user, current_job, organisation_name):
        """Check permissions for creating oauth client"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return {}, 404

        return OrganisationPermissions(
            current_user=current_user,
            organisation=organisation
        ).check_permission(OrganisationPermissions.Permissions.CAN_UPDATE_OAUTH)

    def _post(self, organisation_name, current_user, current_job):
        """Create oauth client"""
        organisation = Organisation.get_by_name_id(organisation_name)

        data = request.json.get("data", {})
        if data.get("type") != "oauth-clients":
            return {}, 400

        attributes = data.get("attributes", {})

        oauth_client = OauthClient.create(
            organisation=organisation,
            name=attributes.get("name"),
            service_provider=OauthServiceProvider(attributes.get("service-provider")),
            key=attributes.get("key"),
            http_url=attributes.get("http-url"),
            api_url=attributes.get("api-url"),
            oauth_token_string=attributes.get("oauth-token-string"),
            private_key=attributes.get("private-key"),
            secret=attributes.get("secret"),
            rsa_public_key=attributes.get("rsa-public-key")
        )

        if not oauth_client:
            return {}, 400

        return {
            "data": oauth_client.get_api_details()
        }


class ApiTerraformOauthClient(AuthenticatedEndpoint):
    """Interface to view/create oauth clients"""

    def check_permissions_get(self, current_user, current_job, oauth_client_id):
        """Check permissions"""
        oauth_client = OauthClient.get_by_api_id(oauth_client_id)
        if not oauth_client:
            return {}, 404

        # @TODO Check this permission
        return OrganisationPermissions(
            current_user=current_user,
            organisation=oauth_client.organisation
        ).check_permission(OrganisationPermissions.Permissions.CAN_ACCESS_VIA_TEAMS)

    def _get(self, oauth_client_id, current_user, current_job):
        """Get list of runs queued"""
        oauth_client = OauthClient.get_by_api_id(oauth_client_id)
        if not oauth_client:
            return {}, 404

        return {
            "data": oauth_client.get_api_details()
        }

    def check_permissions_patch(self, current_user, current_job, oauth_client_id):
        """Check permissions for modifying oauth client"""
        oauth_client = OauthClient.get_by_api_id(oauth_client_id)
        if not oauth_client:
            return {}, 404

        return OrganisationPermissions(
            current_user=current_user,
            organisation=oauth_client.organisation
        ).check_permission(OrganisationPermissions.Permissions.CAN_UPDATE_OAUTH)

    def _patch(self, oauth_client_id, current_user, current_job):
        """Update oauth client"""
        oauth_client = OauthClient.get_by_api_id(oauth_client_id)

        data = request.json.get("data", {})
        if data.get("type") != "oauth-clients":
            return {}, 400

        request_attributes = data.get("attributes", {})

        # Create dictionary of allowed attributes,
        # using mapping of request attribtues to model attributes,
        # adding only if they are present in the request
        update_attributes = {
            target_attribute: request_attributes.get(req_attribute)
            for req_attribute, target_attribute in {
                "name": "name", "key": "key", "secret": "secret", "ras-public-key": "rsa_public_key"
            }.items()
            if req_attribute in request_attributes
        }

        oauth_client.update_attributes(
            **update_attributes
        )

        if not oauth_client:
            return {}, 400

        return {
            "data": oauth_client.get_api_details()
        }

    def check_permissions_delete(self, current_user, current_job, oauth_client_id):
        """Check permissions for modifying oauth client"""
        oauth_client = OauthClient.get_by_api_id(oauth_client_id)
        if not oauth_client:
            return {}, 404

        return OrganisationPermissions(
            current_user=current_user,
            organisation=oauth_client.organisation
        ).check_permission(OrganisationPermissions.Permissions.CAN_UPDATE_OAUTH)

    def _delete(self, oauth_client_id, current_user, current_job):
        """Delete oauth client"""
        oauth_client = OauthClient.get_by_api_id(oauth_client_id)

        oauth_client.delete()

        if not oauth_client:
            return {}, 400


class ApiTerraformPlans(AuthenticatedEndpoint):
    """Interface for plans."""

    def check_permissions_get(self, current_user, current_job, plan_id=None):
        """Check permissions to view run"""
        if not plan_id:
            return False

        plan = Plan.get_by_api_id(plan_id)
        if not plan:
            return {}, 404

        return WorkspacePermissions(
            current_user=current_user,
            workspace=plan.run.configuration_version.workspace
        ).check_access_type(runs=TeamWorkspaceRunsPermission.READ)

    def _get(self, current_user, current_job, plan_id=None):
        """Return information for plan(s)"""
        if plan_id:
            plan = Plan.get_by_api_id(plan_id)
            if not plan:
                return {}, 404

            return {"data": plan.get_api_details()}

        raise Exception('Need to return list of plans?')


class ApiTerraformPlanLog(Resource):
    """
    Interface to obtain logs from stream.
    @TODO: Need to find a way to authenticate this endpoint
    """

    def get(self, plan_id):
        """Return information for plan(s)"""

        parser = reqparse.RequestParser()
        parser.add_argument('offset', type=int, location='args', default=0)
        parser.add_argument('limit', type=int, location='args', default=-1)
        args = parser.parse_args()
        plan = Plan.get_by_api_id(plan_id)
        if not plan:
            return {}, 404

        plan_output = b""
        session = Database.get_session()
        for _ in range(20):
            session.refresh(plan)
            if plan.log:
                session.refresh(plan.log)
                if plan.log.data:
                    plan_output = plan.log.data
                    if args.limit >= 0:
                        plan_output = plan_output[args.offset:(args.offset+args.limit)]
                    else:
                        plan_output = plan_output[args.offset:]
            if plan_output or plan.status not in [
                    TerraformCommandState.PENDING,
                    TerraformCommandState.MANAGE_QUEUED,
                    TerraformCommandState.QUEUED,
                    TerraformCommandState.RUNNING]:
                break
            #print('Waiting as plan state is; ' + str(plan.status))

            sleep(0.2)

        if request.content_type and request.content_type.startswith('text/html'):
            plan_output = plan_output.decode('utf-8')
            plan_output = plan_output.replace(' ', '\u00a0')
            conv = Ansi2HTMLConverter()
            plan_output = conv.convert(plan_output, full=False)
            plan_output = plan_output.replace('\n', '<br/ >')


        response = make_response(plan_output)
        response.headers['Content-Type'] = 'text/plain'
        return response


class ApiTerraformWorkspaceLatestStateVersion(AuthenticatedEndpoint):

    def check_permissions_get(self, current_user, current_job, workspace_id):
        """Check permissions to view run"""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return False

        if current_job and current_job.run.configuration_version.workspace == workspace:
            return True

        return WorkspacePermissions(
            current_user=current_user,
            workspace=workspace
        ).check_access_type(state_versions=TeamWorkspaceStateVersionsPermissions.READ)

    def _get(self, current_user, current_job, workspace_id):
        """Return latest state for workspace."""

        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return {}, 404

        state = Workspace.get_by_api_id(workspace_id).latest_state
        if not state:
            return {}, 404
        
        return {'data': state.get_api_details()}


class ApiTerraformWorkspaceLatestStateVersionOutputs(AuthenticatedEndpoint):

    def check_permissions_get(self, current_user, current_job, workspace_id):
        """Check permissions to view run"""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return False

        if current_job and current_job.run.configuration_version.workspace == workspace:
            return True

        return WorkspacePermissions(
            current_user=current_user,
            workspace=workspace
        ).check_access_type(state_versions=TeamWorkspaceStateVersionsPermissions.READ)

    def _get(self, current_user, current_job, workspace_id):
        """Return latest state for workspace."""

        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return {}, 404

        state = workspace.latest_state
        if not state:
            return {}, 404

        return {'data': [
            output.get_api_details()
            for output in state.state_version_outputs
        ]} #include_sensitive=True


class ApiTerraformWorkspaceActionsLock(AuthenticatedEndpoint):
    """Interface to lock workspace"""

    def check_permissions_post(self, current_user, current_job, workspace_id):
        """Check permissions to lock worksapce"""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return False

        return WorkspacePermissions(
            current_user=current_user,
            workspace=workspace
        ).check_permission(WorkspacePermissions.Permissions.CAN_LOCK)

    def _post(self, current_user, current_job, workspace_id):
        """Lock workspace."""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return {}, 404

        if not workspace.lock(user=current_user, reason=request.json.get("reason")):
            return {
                "errors": [
                    ApiError(
                        "Workspace already locked",
                        "The workspace is already locked, so cannot be locked.",
                        status=409
                    ).get_api_details()
                ]
            }, 409

        return {'data': workspace.get_api_details(effective_user=current_user)[0]}


class ApiTerraformWorkspaceActionsUnlock(AuthenticatedEndpoint):
    """Interface to unlock workspace"""

    def check_permissions_post(self, current_user, current_job, workspace_id):
        """Check permissions to unlock worksapce"""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return False

        return WorkspacePermissions(
            current_user=current_user,
            workspace=workspace
        ).check_permission(WorkspacePermissions.Permissions.CAN_UNLOCK)

    def _post(self, current_user, current_job, workspace_id):
        """Return latest state for workspace."""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return {}, 404

        if not workspace.unlock(user=current_user):
            return {
                "errors": [ApiError(
                    "Unable to unlock workspace",
                    "The workspace is not locked or the lock is held by another user"
                )]
            }, 422

        return {'data': workspace.get_api_details(effective_user=current_user)[0]}


class ApiTerraformWorkspaceActionsForceUnlock(AuthenticatedEndpoint):
    """Interface to unlock workspace"""

    def check_permissions_post(self, current_user, current_job, workspace_id):
        """Check permissions to unlock worksapce"""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return False

        return WorkspacePermissions(
            current_user=current_user,
            workspace=workspace
        ).check_permission(WorkspacePermissions.Permissions.CAN_FORCE_UNLOCK)

    def _post(self, current_user, current_job, workspace_id):
        """Return latest state for workspace."""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return {}, 404

        workspace.unlock(force=True)

        return {'data': workspace.get_api_details(effective_user=current_user)[0]}


class ApiTerraformWorkspaceStates(AuthenticatedEndpoint):
    """Interface to list/create state versions"""

    def check_permissions_post(self, current_user, current_job, workspace_id):
        """Check permissions to create state versions"""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return False

        if current_job and current_job.run.configuration_version.workspace == workspace:
            return True

        return WorkspacePermissions(
            current_user=current_user,
            workspace=workspace
        ).check_access_type(state_versions=TeamWorkspaceStateVersionsPermissions.WRITE)

    def _post(self, current_user, current_job, workspace_id):
        """Create new state version for workspace."""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return {}, 404

        data = request.json.get("data", {})
        # @TODO Handle this more nicely
        assert data.get("type") == "state-versions"

        state_base64 = data.get("attributes", {}).get("state", None)
        if not state_base64:
            param_error = ApiError(
                title = "param is missing or the value is empty: state",
                details = "Terrarun does not support state upload directly to storage.",
                status = 400,
                pointer="/data/attributes/state",
            )
            return ApiErrorView(error=param_error).to_response(code = 400)

        run_id = data.get("relationships", {}).get("run", {}).get("data", {}).get("id", None)
        run = None
        if run_id:
            run = Run.get_by_api_id(run_id)
            if run is None:
                return {}, 400

        # Attempt to get current run based on job authentication
        if not run_id and current_job:
            run = current_job.run
            
        created_by = current_user if current_user is not None else run.created_by if run is not None else None

        state_version = StateVersion.create_from_state_json(
            workspace=workspace,
            run=run,
            created_by=created_by,
            state_json=json.loads(base64.b64decode(state_base64).decode('utf-8'))
        )
        if not state_version:
            return {}, 400

        if run:
            # Update run with state version
            run.plan.apply.update_attributes(state_version=state_version)

        return {'data': state_version.get_api_details()}


class ApiTerraformStateVersionDownload(AuthenticatedEndpoint):

    def check_permissions_get(self, current_user, current_job, state_version_id):
        """Check permissions to read state versions"""
        state_version = StateVersion.get_by_api_id(state_version_id)
        if not state_version:
            return False

        if current_job and current_job.run.configuration_version.workspace == state_version.workspace:
            return True

        return WorkspacePermissions(
            current_user=current_user,
            workspace=state_version.workspace
        ).check_access_type(state_versions=TeamWorkspaceStateVersionsPermissions.READ)

    def _get(self, current_user, current_job, state_version_id):
        """Return state version json"""
        state_version = StateVersion.get_by_api_id(state_version_id)
        if not state_version_id:
            return {}, 404
        return state_version.state_json


class ApiTerraformStateVersionOutput(AuthenticatedEndpoint):
    """Interface to read state version outputs"""

    def check_permissions_get(self, current_user, current_job, state_version_output_id):
        """Check permissions to view state version output"""
        state_version_output = StateVersionOutput.get_by_api_id(state_version_output_id)
        if not state_version_output:
            return False

        return WorkspacePermissions(
            current_user=current_user,
            workspace=state_version_output.state_version.workspace
        ).check_access_type(state_versions=TeamWorkspaceStateVersionsPermissions.READ)

    def _get(self, current_user, current_job, state_version_output_id):
        """Return state version json"""
        state_version_output = StateVersionOutput.get_by_api_id(state_version_output_id)
        if not state_version_output:
            return {}, 404
        return {"data": state_version_output.get_api_details(include_sensitive=True)}


class ApiTerraformIngressAttribute(AuthenticatedEndpoint):
    """Interface to interact with ingress attributes"""

    def check_permissions_get(self, current_user, current_job, ingress_attribute_id):
        """Check permissions to view ingress attribute"""
        ingress_attribute = IngressAttribute.get_by_api_id(ingress_attribute_id)
        if not ingress_attribute:
            return False

        return OrganisationPermissions(
            current_user=current_user,
            organisation=ingress_attribute.authorised_repo.oauth_token.oauth_client.organisation
        ).check_permission(OrganisationPermissions.Permissions.CAN_ACCESS_VIA_TEAMS)

    def _get(self, current_user, current_job, ingress_attribute_id):
        """Return state version json"""
        ingress_attribute = IngressAttribute.get_by_api_id(ingress_attribute_id)
        if not ingress_attribute:
            return {}, 404
        return {"data": ingress_attribute.get_api_details()}


class ApiTerraformApplyRun(AuthenticatedEndpoint):
    """Interface to confirm run"""

    def check_permissions_post(self, current_user, current_job, run_id):
        """Check permissions to view run"""
        run = Run.get_by_api_id(run_id)
        if not run:
            return False

        return WorkspacePermissions(
            current_user=current_user,
            workspace=run.configuration_version.workspace
        ).check_access_type(runs=TeamWorkspaceRunsPermission.APPLY)

    def _post(self, current_user, current_job, run_id):
        """Initialise run apply."""
        run = Run.get_by_api_id(run_id)
        if not run:
            return {}, 404
        run.confirm(comment=flask.request.get_json().get('comment', None), user=current_user)
        return {}, 202


class ApiTerraformApplies(AuthenticatedEndpoint):
    """Interface for applies"""

    def check_permissions_get(self, current_user, current_job, apply_id=None):
        """Check permissions to view run"""
        if not apply_id:
            raise Exception('IT WAS CALLED')

        apply = Apply.get_by_api_id(apply_id)
        if not apply:
            return False

        return WorkspacePermissions(
            current_user=current_user,
            workspace=apply.plan.run.configuration_version.workspace
        ).check_access_type(runs=TeamWorkspaceRunsPermission.READ)

    def _get(self, current_user, current_job, apply_id=None):
        """Get apply details."""
        if not apply_id:
            raise Exception('IT WAS CALLED')

        apply = Apply.get_by_api_id(apply_id)
        if not apply:
            return {}, 404
        
        return {'data': apply.get_api_details()}


class ApiTerraformApplyLog(Resource):
    """
    Interface to obtain logs from stream.
    @TODO: Need to find a way to authenticate this endpoint
    """

    def get(self, apply_id):
        """Return information for plan(s)"""

        parser = reqparse.RequestParser()
        parser.add_argument('offset', type=int, location='args', default=0)
        parser.add_argument('limit', type=int, location='args', default=-1)
        args = parser.parse_args()
        apply = Apply.get_by_api_id(apply_id)
        if not apply:
            return {}, 404

        output = b""
        session = Database.get_session()
        for _ in range(20):
            session.refresh(apply)
            if apply.log:
                session.refresh(apply.log)

                if apply.log.data:
                    output = apply.log.data
                    if args.limit >= 0:
                        output = output[args.offset:(args.offset+args.limit)]
                    else:
                        output = output[args.offset:]

            # If output has been captured or command has finished or
            # limit is -1 (i.e. not a call from terraform), return
            # and do not wait for (more) output
            if output or args.limit == -1 or apply.status not in [
                    TerraformCommandState.PENDING,
                    TerraformCommandState.MANAGE_QUEUED,
                    TerraformCommandState.QUEUED,
                    TerraformCommandState.RUNNING]:
                break
            #print('Waiting as apply state is; ' + str(apply.status))

            sleep(0.2)

        if request.content_type and request.content_type.startswith('text/html'):
            output = output.decode('utf-8')
            output = output.replace(' ', '\u00a0')
            conv = Ansi2HTMLConverter()
            output = conv.convert(output, full=False)
            output = output.replace('\n', '<br/ >')

        response = make_response(output)
        response.headers['Content-Type'] = 'text/plain'
        return response


class ApiTerrarunOrganisationCreateNameValidation(AuthenticatedEndpoint):
    """Endpoint to validate new organisation name"""

    def check_permissions_post(self, current_user, current_job):
        """Check permissions"""
        return UserPermissions(current_user=current_user, user=current_user).check_permission(
            UserPermissions.Permissions.CAN_CREATE_ORGANISATIONS)

    def _post(self, current_user, current_job):
        """Validate new organisation name"""
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, location='json')
        args = parser.parse_args()
        name_id = Organisation.name_to_name_id(args.name)
        
        return {
            "data": {
                "valid": Organisation.validate_new_name_id(name_id),
                "name": args.name,
                "name_id": name_id
            }
        }


class ApiTerrarunProjectCreateNameValidation(AuthenticatedEndpoint):
    """Endpoint to validate new workspace name"""

    def check_permissions_post(self, organisation_name, current_user, current_job):
        """Check permissions"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return False
        return OrganisationPermissions(current_user=current_user, organisation=organisation).check_permission(
            OrganisationPermissions.Permissions.CAN_CREATE_WORKSPACE)

    def _post(self, organisation_name, current_user, current_job):
        """Validate new organisation name"""
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, location='json')
        args = parser.parse_args()

        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return {}, 404

        return {
            "data": {
                "valid": Project.validate_new_name(organisation, args.name),
                "name": args.name
            }
        }


class ApiTerrarunWorkspaceCreateNameValidation(AuthenticatedEndpoint):
    """Endpoint to validate new workspace name"""

    def check_permissions_post(self, organisation_name, current_user, current_job):
        """Check permissions"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return False
        return OrganisationPermissions(current_user=current_user, organisation=organisation).check_permission(
            OrganisationPermissions.Permissions.CAN_CREATE_WORKSPACE)

    def _post(self, organisation_name, current_user, current_job):
        """Validate new organisation name"""
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, location='json')
        args = parser.parse_args()

        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return {}, 404

        return {
            "data": {
                "valid": Workspace.validate_new_name(organisation, args.name),
                "name": args.name
            }
        }


class ApiTerrarunTaskCreateNameValidation(AuthenticatedEndpoint):
    """Endpoint to validate new task name"""

    def check_permissions_post(self, organisation_name, current_user, current_job):
        """Check permissions"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return False
        return OrganisationPermissions(current_user=current_user, organisation=organisation).check_permission(
            OrganisationPermissions.Permissions.CAN_MANAGE_RUN_TASKS)

    def _post(self, organisation_name, current_user, current_job):
        """Validate new task name"""
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, location='json')
        args = parser.parse_args()

        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return {}, 404

        return {
            "data": {
                "valid": Task.validate_new_name(organisation, args.name),
                "name": args.name
            }
        }

class ApiTerrarunEnvironmentCreateNameValidation(AuthenticatedEndpoint):
    """Endpoint to validate new environment name"""

    def check_permissions_post(self, organisation_name, current_user, current_job):
        """Check permissions"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return False
        return OrganisationPermissions(current_user=current_user, organisation=organisation).check_permission(
            OrganisationPermissions.Permissions.CAN_MANAGE_RUN_TASKS)

    def _post(self, organisation_name, current_user, current_job):
        """Validate new environment name"""
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, location='json')
        args = parser.parse_args()

        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return {}, 404

        return {
            "data": {
                "valid": Environment.validate_new_name(organisation, args.name),
                "name": args.name
            }
        }


class ApiTerrarunLifecycleCreateNameValidation(AuthenticatedEndpoint):
    """Endpoint to validate new environment lifecycle name"""

    def check_permissions_post(self, organisation_name, current_user, current_job):
        """Check permissions"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return False
        return OrganisationPermissions(current_user=current_user, organisation=organisation).check_permission(
            OrganisationPermissions.Permissions.CAN_MANAGE_VARSETS)

    def _post(self, organisation_name, current_user, current_job):
        """Validate new environment name"""
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, location='json')
        args = parser.parse_args()

        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return {}, 404

        return {
            "data": {
                "valid": Lifecycle.validate_new_name(organisation, args.name),
                "name": args.name
            }
        }


class ApiTerraformWorkspaceTasks(AuthenticatedEndpoint):
    """Interface to manage workspace tasks"""

    def check_permissions_get(self, workspace_id, current_user, current_job):
        """Check permissions"""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return False
        return WorkspacePermissions(
            current_user=current_user, workspace=workspace
        ).check_permission(WorkspacePermissions.Permissions.CAN_READ_SETTINGS)

    def _get(self, workspace_id, current_user, current_job):
        """Return list of workspace tasks"""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return {}, 404
        
        return {
            "data": [
                workspace_task.get_api_details()
                for workspace_task in workspace.workspace_tasks
                if workspace_task.active
            ],
            "links": {
                "self": "https://app.terraform.io/api/v2/workspaces/ws-kRsDRPtTmtcEme4t/tasks?page%5Bnumber%5D=1&page%5Bsize%5D=20",
                "first": "https://app.terraform.io/api/v2/workspaces/ws-kRsDRPtTmtcEme4t/tasks?page%5Bnumber%5D=1&page%5Bsize%5D=20",
                "prev": None,
                "next": None,
                "last": "https://app.terraform.io/api/v2/workspaces/ws-kRsDRPtTmtcEme4t/tasks?page%5Bnumber%5D=1&page%5Bsize%5D=20"
            },
            "meta": {
                # @TODO populate and respect pagination
                "pagination": {
                    "current-page": 1,
                    "page-size": 20,
                    "prev-page": None,
                    "next-page": None,
                    "total-pages": 1,
                    "total-count": 1
                }
            }
        }

    def check_permissions_post(self, workspace_id, current_user, current_job):
        """Check permissions"""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return False
        return WorkspacePermissions(
            current_user=current_user, workspace=workspace
        ).check_permission(WorkspacePermissions.Permissions.CAN_MANAGE_RUN_TASKS)

    def _post(self, workspace_id, current_user, current_job):
        """Associate a task with a workspace"""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return {}, 404

        data = flask.request.get_json().get("data", {})
        if data.get("type") != "workspace-tasks":
            return {}, 400

        attributes = data.get("attributes", {})
        task_data = data.get("relationships", {}).get("task", {}).get("data", {})
        if task_data.get("type") != "tasks":
            return {}, 400

        task_id = task_data.get("id")
        if not task_id:
            return {}, 400
        
        task = Task.get_by_api_id(task_id)

        workspace_task = workspace.associate_task(
            task=task,
            enforcement_level=WorkspaceTaskEnforcementLevel(attributes.get("enforcement-level")),
            stage=WorkspaceTaskStage(attributes.get('stage', WorkspaceTaskStage.POST_PLAN.value))
        )
        return workspace_task.get_api_details()


class ApiTerraformWorkspaceTask(AuthenticatedEndpoint):
    """Interface to manage workspace task"""

    def check_permissions_get(self, workspace_id, workspace_task_id, current_user, current_job):
        """Check permissions"""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return False
        return WorkspacePermissions(
            current_user=current_user, workspace=workspace
        ).check_permission(WorkspacePermissions.Permissions.CAN_READ_SETTINGS)

    def _get(self, workspace_id, workspace_task_id, current_user, current_job):
        """Return list of workspace tasks"""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return {}, 404

        workspace_task = WorkspaceTask.get_by_api_id(workspace_task_id)
        # Ensure workspace task exists and it's associated with the
        # specified workspace
        if not workspace_task or workspace_task.workspace.id != workspace.id:
            return {}, 404

        return {
            "data": workspace_task.get_api_details()
        }

    def check_permissions_delete(self, workspace_id, workspace_task_id, current_user, current_job):
        """Check permissions"""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return False
        return WorkspacePermissions(
            current_user=current_user, workspace=workspace
        ).check_permission(WorkspacePermissions.Permissions.CAN_MANAGE_RUN_TASKS)

    def _delete(self, workspace_id, workspace_task_id, current_user, current_job):
        """Associate a task with a workspace"""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return {}, 404

        workspace_task = WorkspaceTask.get_by_api_id(workspace_task_id)
        # Ensure workspace task exists and it's associated with the
        # specified workspace
        if not workspace_task or workspace_task.workspace.id != workspace.id:
            return {}, 404

        workspace_task.delete()


class ApiTerraformTaskResults(AuthenticatedEndpoint):
    """Interface to handle details/callbacks for task results"""

    def check_permissions_get(self, task_result_id, current_user, current_job):
        task_result = TaskResult.get_by_api_id(task_result_id)
        if not task_result:
            return False

        return WorkspacePermissions(
            current_user=current_user,
            workspace=task_result.task_stage.run.configuration_version.workspace
        ).check_access_type(runs=TeamWorkspaceRunsPermission.READ)

    def _get(self, task_result_id, current_user, current_job):
        """Get task result details"""
        task_result = TaskResult.get_by_api_id(task_result_id)
        if not task_result:
            return {}, 422

        return {'data': task_result.get_api_details()}

    def check_permissions_patch(self, task_result_id, current_user, current_job):
        task_result = TaskResult.get_by_callback_id(task_result_id)
        if not task_result:
            return False

        run = task_result.task_stage.run
        if not run:
            return False

        return current_user.has_task_execution_run_access(run=run)

    def _patch(self, task_result_id, current_user, current_job):
        """Update details from callback from task executor"""
        task_result = TaskResult.get_by_callback_id(task_result_id)
        if not task_result:
            return {}, 422

        data = flask.request.get_json().get("data", {})

        if data.get("type") != "task-results":
            return {}, 422
        attributes = data.get("attributes", {})

        task_result.handle_callback(
            status=TaskResultStatus(attributes.get("status")),
            message=attributes.get("message"),
            url=attributes.get("url"))

        return {}, 200


class ApiTerraformRunTaskStages(AuthenticatedEndpoint):
    """Interface to view run task stages"""

    def check_permissions_get(self, run_id, current_user, current_job):
        """Check permissions"""
        run = Run.get_by_api_id(run_id)
        if not run:
            return False
        return WorkspacePermissions(
            current_user=current_user,
            workspace=run.configuration_version.workspace
        ).check_access_type(runs=TeamWorkspaceRunsPermission.READ)

    def _get(self, run_id, current_user, current_job):
        """Return list of run task stages"""
        run = Run.get_by_api_id(run_id)
        if not run:
            return {}, 404

        return {
            "data": [
                task_stage.get_api_details()
                for task_stage in run.task_stages
            ]
        }



class ApiTerraformTaskStage(AuthenticatedEndpoint):
    """Interface to view task stage"""

    def check_permissions_get(self, task_stage_id, current_user, current_job):
        """Check permissions"""
        task_stage = TaskStage.get_by_api_id(task_stage_id)
        if not task_stage:
            return False
        return WorkspacePermissions(
            current_user=current_user,
            workspace=task_stage.run.configuration_version.workspace
        ).check_access_type(runs=TeamWorkspaceRunsPermission.READ)

    def _get(self, task_stage_id, current_user, current_job):
        """Return list of run task stages"""
        task_stage = TaskStage.get_by_api_id(task_stage_id)
        if not task_stage:
            return {}, 404

        return {
            "data": task_stage.get_api_details()
        }


class ApiOrganisationAgentPoolList(AuthenticatedEndpoint):
    """Interface to interact with organisation agent pools"""

    def check_permissions_get(self, organisation_name, current_user, current_job):
        """Check permissions"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return False
        return OrganisationPermissions(
            current_user=current_user,
            organisation=organisation
        ).check_permission(
            OrganisationPermissions.Permissions.CAN_ACCESS_VIA_TEAMS
        )
    
    def _get(self, organisation_name, current_user, current_job):
        """Get list of agent pools for organisation"""
        organisation = Organisation.get_by_name_id(organisation_name)
        agent_pools = AgentPool.get_by_organisation(organisation=organisation, include_global=True)
        return {
            "data": [
                agent_pool.get_api_details()
                for agent_pool in agent_pools
            ],
            "links": {
            },
            "meta": {
                "pagination": {
                    "current-page": 1,
                    "prev-page": None,
                    "next-page": None,
                    "total-pages": 1,
                    "total-count": len(agent_pools)
                },
                "status-counts": {
                    "total": len(agent_pools),
                    "matching": len(agent_pools)
                }
            }
        }


class ApiOrganisationAgentPool(AuthenticatedEndpoint):
    """Interface to interact with agent pool"""

    def check_permissions_get(self, agent_pool_id, current_user, current_job):
        """Check permissions"""
        agent_pool = AgentPool.get_by_api_id(agent_pool_id)
        if not agent_pool:
            return False

        if agent_pool.organisation:
            return OrganisationPermissions(
                current_user=current_user,
                organisation=agent_pool.organisation
            ).check_permission(
                OrganisationPermissions.Permissions.CAN_ACCESS_VIA_TEAMS
            )
        else:
            # Allow all users to view agent pools not associated with an organisation
            return True
    
    def _get(self, agent_pool_id, current_user, current_job):
        """Get list of agent pools for organisation"""
        agent_pool = AgentPool.get_by_api_id(agent_pool_id)
        view = AgentPoolView.from_object(agent_pool, effective_user=current_user)
        return view.to_response()


class AgentEndpoint:

    def _get_agent_token(self):
        """Obtain agent token from authorization bearer header"""
        # Get agent token
        if not (auth_token_match := re.match(r'^Bearer (.*)$', request.headers.get('Authorization', ''))):
            return None
        
        request_agent_token = auth_token_match.group(1)

        return AgentToken.get_by_token(request_agent_token) 

    def _get_agent(self):
        """Obtain agent object from request"""
        # Get agent token
        agent_token = self._get_agent_token()
        if not agent_token:
            return None

        if not (agent_id := request.headers.get("Tfc-Agent-Id", "")):
            return None

        agent = Agent.get_by_agent_pool_and_api_id(api_id=agent_id, agent_pool=agent_token.agent_pool)
        return agent


class ApiAgentRegister(Resource, AgentEndpoint):
    """Interface to register agent"""

    def post(self):
        agent_token = self._get_agent_token()
        if not agent_token:
            return {}, 403
        
        agent = Agent.register_agent(
            agent_token=agent_token,
            name=request.headers.get('Host')
        )

        return {
            "id": agent.api_id,
            "pool_id": agent_token.agent_pool.api_id
        }, 200


class ApiAgentStatus(Resource, AgentEndpoint):
    """Interface to update agent status"""

    def put(self):
        """Update agent status"""
        agent = self._get_agent()
        if not agent:
            return {}, 403

        try:
            agent_status = AgentStatus(request.json.get("status", ""))
        except ValueError:
            return {}, 400

        if job_status := request.json.get("job"):
            # Get plan
            if job_status.get("type") == "plan":
                JobProcessor.handle_plan_status_update(job_status)
            elif job_status.get("type") == "apply":
                JobProcessor.handle_apply_status_update(job_status)
            else:
                logger.error("Unknown job type: %s", job_status.get('type'))
                return {}, 500

        agent.update_status(
            agent_status
        )

        res = make_response({}, 200)
        # @TODO Confirm what this is.. does it ever get passed as a non-zero number?
        res.headers['Tfc-Agent-Message-Index'] = request.headers.get('Tfc-Agent-Message-Index', 0)
        return res


class ApiAgentJobs(Resource, AgentEndpoint):
    """Interface to update agent status"""

    def get(self):
        """Get list of jobs to be run"""
        accepted_job_types_raw = request.headers.get('Tfc-Agent-Accept', '').split(',')
        accepted_job_types = [
            JobQueueType(accepted_job_type_raw)
            for accepted_job_type_raw in accepted_job_types_raw
        ]


        agent = self._get_agent()
        if not agent:
            return {}, 403

        job = JobProcessor.get_job_by_agent_and_job_types(agent=agent, job_types=accepted_job_types)

        if job:
            if job.job_type is JobQueueType.PLAN:
                # @TODO: Work out what state showing the plan
                # has been assigned to an agent
                pass
            elif job.job_type is JobQueueType.APPLY:
                # @TODO: Work out what state showing the apply
                # has been assigned to an agent
                pass
            else:
                logger.error('Job (id: %s) does not have a valid job_type: %s', job.id, job.job_type)
                return {}, 204

            tool = job.run.tool if job.run.tool else job.run.configuration_version.workspace.tool

            # Generate user token for run
            token = UserToken.create_agent_job_token(job=job)

            presign = Presign()
            run_key = presign.encrypt(job.run.api_id)

            # Either the plan or apply api ID
            job_sub_task_id = job.run.plan.api_id if job.job_type is JobQueueType.PLAN else job.run.plan.apply.api_id

            return {
                # @TODO Should this be apply for plans during an apply run?
                "type": job.job_type.value,
                "data": {
                    "run_id": job.run.api_id,
                    # @TODO Should this be apply for plans during an apply run?
                    "operation": job.job_type.value,
                    "organization_name": job.run.configuration_version.workspace.organisation.name_id,
                    "workspace_name": job.run.configuration_version.workspace.name,
                    "terraform_url": tool.get_presigned_download_url(),
                    "terraform_checksum": tool.get_checksum(),
                    "terraform_log_url": f"{terrarun.config.Config().BASE_URL}/api/agent/log/{job.job_type.value}/{job_sub_task_id}?key={run_key}",
                    "configuration_version_url": job.run.configuration_version.get_download_url(),
                    "filesystem_url": f"{terrarun.config.Config().BASE_URL}/api/agent/filesystem?key={run_key}",
                    "token": token.token,
                    "destroy": job.run.is_destroy,
                    "target_addrs": job.run.target_addrs,
                    "refresh_only": job.run.refresh_only,
                    "timeout": "{}s".format(terrarun.config.Config().AGENT_JOB_TIMEOUT),
                    "json_plan_url": f"{terrarun.config.Config().BASE_URL}/api/v2/plans/{job.run.plan.api_id}/json-output",
                    "json_provider_schemas_url": f"{terrarun.config.Config().BASE_URL}/api/v2/plans/{job.run.plan.api_id}/json-providers-schemas"
                }
            }, 200

        # Return no jobs
        return {}, 204


class ApiAgentPlanLog(Resource):
    """Interface to upload terraform logs"""

    def put(self, plan_id):
        """Handle log upload"""
        decrypted_run_id = Presign().decrypt(request.args.get('key', ''))
        if not decrypted_run_id:
            return {}, 404

        plan = Plan.get_by_api_id(plan_id)
        if not plan:
            return {}, 404

        # Check encrypted run ID in URL
        if plan.run.api_id != decrypted_run_id:
            return {}, 404

        plan.append_output(request.data, no_append=True)
        return {}, 200

    def patch(self, plan_id):
        """Handle log upload"""
        decrypted_run_id = Presign().decrypt(request.args.get('key', ''))
        if not decrypted_run_id:
            return {}, 404

        plan = Plan.get_by_api_id(plan_id)
        if not plan:
            return {}, 404

        # Check encrypted run ID in URL
        if plan.run.api_id != decrypted_run_id:
            return {}, 404

        plan.append_output(request.data)
        return {}, 200


class ApiAgentApplyLog(Resource):
    """Interface to upload terraform logs"""

    def put(self, apply_id):
        """Handle log upload"""
        decrypted_run_id = Presign().decrypt(request.args.get('key', ''))
        if not decrypted_run_id:
            return {}, 404

        apply = Apply.get_by_api_id(apply_id)
        if not apply:
            return {}, 404

        # Check encrypted run ID in URL
        if apply.plan.run.api_id != decrypted_run_id:
            return {}, 404

        apply.append_output(request.data, no_append=True)
        return {}, 200

    def patch(self, apply_id):
        """Handle log upload"""
        decrypted_run_id = Presign().decrypt(request.args.get('key', ''))
        if not decrypted_run_id:
            return {}, 404

        apply = Apply.get_by_api_id(apply_id)
        if not apply:
            return {}, 404

        # Check encrypted run ID in URL
        if apply.plan.run.api_id != decrypted_run_id:
            return {}, 404

        apply.append_output(request.data)
        return {}, 200


class ApiAgentFilesystem(Resource):
    """Interface to download base filesystem for agent"""

    def get(self):
        """Return filesystem for agent"""
        # Obtain run ID from presigned URL
        run_id = Presign().decrypt(request.args.get('key', ''))
        if not run_id:
            return {}, 404

        # Obtain run and error on non-existent run        
        run = Run.get_by_api_id(run_id)
        if not run:
            return {}, 404

        agent_filesystem = AgentFilesystem(run=run)
        return make_response(agent_filesystem.get_content())

    def put(self):
        """Handle upload of new filesystem image"""
        # @TODO Populate this and perform authentication
        # Obtain run ID from presigned URL
        run_id = Presign().decrypt(request.args.get('key', ''))
        if not run_id:
            return {}, 404

        # Obtain run and error on non-existent run        
        run = Run.get_by_api_id(run_id)
        if not run:
            return {}, 404

        agent_filesystem = AgentFilesystem(run=run)
        agent_filesystem.upload_content(request.data)
        return {}, 200


class ApiTerraformPlanJsonOutput(Resource):
    """Interface to push/get JSON plan output"""

    def put(self, plan_id):
        """Handle upload of plan json output"""
        # @TODO Add authentication to this
        plan_json_blob = request.data.decode('utf-8')
        plan_json = json.loads(plan_json_blob)
        plan = Plan.get_by_api_id(plan_id)
        if not plan:
            return {}, 404
        plan.plan_output = plan_json


class ApiTerraformPlanJsonProvidersSchemas(Resource):
    """Interface to push/get JSON plan providers schema"""

    def put(self, plan_id):
        # @TODO Add authentication to this
        providers_schemas_json_blob = request.data.decode('utf-8')
        providers_schemas_json = json.loads(providers_schemas_json_blob)
        plan = Plan.get_by_api_id(plan_id)
        if not plan:
            return {}, 404
        plan.providers_schemas = providers_schemas_json


class OauthAuthorise(Resource):
    """Provide redirect to oauth authorisation flow"""

    def get(self, callback_uuid):
        """Provide redirect to oauth endpoint"""
        oauth_client = OauthClient.get_by_callback_uuid(callback_uuid)
        if not oauth_client:
            return {}, 404

        response_object, session_changes = oauth_client.service_provider_instance.get_authorise_response_object()
        session.update(**session_changes)
        session.modified = True
        return response_object


class OauthAuthoriseCallback(AuthenticatedEndpoint):
    """Provide interface to handle oauth callbacks"""

    def check_permissions_get(self, current_user, current_job, callback_uuid):
        oauth_client = OauthClient.get_by_callback_uuid(callback_uuid)
        if not oauth_client:
            return False

        return OrganisationPermissions(organisation=oauth_client.organisation, current_user=current_user).check_permission(
            OrganisationPermissions.Permissions.CAN_UPDATE_OAUTH)

    def _get(self, callback_uuid, current_user, current_job):
        """Handle oauth callback"""
        oauth_client = OauthClient.get_by_callback_uuid(callback_uuid)
        if not oauth_client:
            return {}, 404

        oauth_token = oauth_client.service_provider_instance.handle_authorise_callback(
            current_user=current_user,
            request=request,
            request_session=session
        )
        if not oauth_token:
            return {}, 400

        return {"staus": "ok", "message": "Please close this window"}, 200


class ApiOauthTokenAuthorisedRepos(AuthenticatedEndpoint):
    """Interface to obtain repositories using oauth token"""

    def check_permissions_get(self, current_user, current_job, oauth_token_id):
        oauth_token = OauthToken.get_by_api_id(oauth_token_id)
        if not oauth_token:
            return False

        return OrganisationPermissions(organisation=oauth_token.oauth_client.organisation, current_user=current_user).check_permission(
            OrganisationPermissions.Permissions.CAN_ACCESS_VIA_TEAMS)

    def _get(self, current_user, current_job, oauth_token_id):
        """Obtain list of repositories provided by oauth client"""
        oauth_token = OauthToken.get_by_api_id(oauth_token_id)
        if not oauth_token:
            return False

        return {
            "data": oauth_token.oauth_client.get_repositories_api_details(oauth_token)
        }


class ApiToolVersions(AuthenticatedEndpoint):
    """Interface to view tool versions"""
    def check_permissions_get(self, current_user, current_job):
        """Can be access by any logged in user"""
        return bool(current_user)

    def _get(self, current_user, current_job):
        """Provide list of terraform versions"""

        return {
            "data": [
                tool.get_api_details()
                for tool in Tool.get_list(tool_type=ToolType.TERRAFORM_VERSION)
            ]
        }

