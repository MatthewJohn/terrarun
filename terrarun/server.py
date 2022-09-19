# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import json
import queue
import re
import threading
from time import sleep
import traceback

from flask import Flask, make_response, request
from sqlalchemy import desc
from sqlalchemy.orm import scoped_session
import flask
from flask_cors import CORS
from flask_restful import Api, Resource, marshal_with, reqparse, fields
from ansi2html import Ansi2HTMLConverter

from terrarun import workspace
from terrarun.apply import Apply
from terrarun.audit_event import AuditEvent
from terrarun.configuration import ConfigurationVersion
from terrarun.database import Database
from terrarun.organisation import Organisation
from terrarun.permissions.organisation import OrganisationPermissions
from terrarun.permissions.user import UserPermissions
from terrarun.permissions.workspace import WorkspacePermissions
from terrarun.plan import Plan
from terrarun.run import Run
from terrarun.run_queue import RunQueue
from terrarun.state_version import StateVersion
from terrarun.tag import Tag
from terrarun.task import Task
from terrarun.terraform_command import TerraformCommandState
from terrarun.user_token import UserToken, UserTokenType
from terrarun.workspace import Workspace
from terrarun.user import User
from terrarun.team_workspace_access import TeamWorkspaceAccess, TeamWorkspaceRunsPermission, TeamWorkspaceStateVersionsPermissions
from terrarun.team_user_membership import TeamUserMembership
from terrarun.team import Team
from terrarun.workspace_task import WorkspaceTask, WorkspaceTaskEnforcementLevel, WorkspaceTaskStage


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
            '/api/v2/organizations/<string:organisation_name>/workspaces/<string:workspace_name>'
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
            ApiTerraformWorkspaceConfigurationVersions,
            '/api/v2/workspaces/<string:workspace_id>/configuration-versions'
        )
        self._api.add_resource(
            ApiTerraformWorkspaceLatestStateVersion,
            '/api/v2/workspaces/<string:workspace_id>/current-state-version'
        )
        self._api.add_resource(
            ApiTerraformWorkspaceRelationshipsTags,
            '/api/v2/workspaces/<string:workspace_id>/relationships/tags'
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
            ApiTerraformRunAuditEvents,
            '/api/v2/runs/<string:run_id>/relationships/audit-events'
        )
        self._api.add_resource(
            ApiTerraformRunActionsCancel,
            '/api/v2/runs/<string:run_id>/actions/cancel'
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
            ApiTerraformPlans,
            '/api/v2/plans',
            '/api/v2/plans/<string:plan_id>'
        )
        self._api.add_resource(
            ApiTerraformPlanLog,
            '/api/v2/plans/<string:plan_id>/log'
        )
        self._api.add_resource(
            ApiTerraformStateVersionDownload,
            '/api/v2/state-versions/<string:state_version_id>/download'
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

        # Custom endpoints
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
            ApiTerrarunTaskCreateNameValidation,
            '/api/terrarun/v1/organisation/<string:organisation_name>/task-name-validate'
        )

    def run(self, debug=None):
        """Run flask server."""
        kwargs = {
            'host': self.host,
            'port': self.port,
            'debug': True,
            'threaded': True
        }
        if self.ssl_public_key and self.ssl_private_key:
            kwargs['ssl_context'] = (self.ssl_public_key, self.ssl_private_key)

        self._app.secret_key = "abcefg"

        self.queue_run = True
        self.worker_thread = threading.Thread(target=self.worker, daemon=True).start()
        self._app.run(**kwargs)
        self.queue_run = False

    def worker(self):
        """Run worker queue"""
        while self.queue_run:
            try:
                session = Database.get_session()
                rq = session.query(RunQueue).first()
                if not rq:
                    sleep(5)
                    continue

                run = rq.run
                session.delete(rq)
                session.commit()
                print("Worker, found run: " + run.api_id)
                run.execute_next_step()
            except Exception as exc:
                print('Error during worker run: ' + str(exc))
                print(traceback.format_exc())


class AuthenticatedEndpoint(Resource):
    """Authenticated endpoint"""

    def _get_current_user(self):
        """Obtain current user based on API token key in request"""
        authorization_header = request.headers.get('Authorization', '')
        auth_token = re.sub(r'^Bearer ', '', authorization_header)
        user_token = UserToken.get_by_token(auth_token)
        if not user_token:
            return None
        return user_token.user

    def _get(self, *args, **kwargs):
        """Handle GET request method to re-implemented by overriding class."""
        raise NotImplementedError

    def check_permissions_get(self, *args, **kwargs):
        """Function to check permissions, must be implemented by overriding class."""
        raise NotImplementedError

    def get(self, *args, **kwargs):
        """Handle GET request"""
        current_user = self._get_current_user()
        if not current_user:
            print('No user')
            return {}, 403

        if not self.check_permissions_get(*args, current_user=current_user, **kwargs):
            return {}, 404

        return self._get(*args, current_user=current_user, **kwargs)

    def _post(self, *args, **kwargs):
        """Handle POST request method to re-implemented by overriding class."""
        raise NotImplementedError

    def check_permissions_post(self, *args, **kwargs):
        """Function to check permissions, must be set by implementer"""
        raise NotImplementedError

    def post(self, *args, **kwargs):
        """Handle POST request"""
        current_user = self._get_current_user()
        if not current_user:
            return {}, 403

        if not self.check_permissions_post(*args, current_user=current_user, **kwargs):
            return {}, 404
        return self._post(*args, current_user=current_user, **kwargs)

    def _patch(self, *args, **kwargs):
        """Handle PATCH request method to re-implemented by overriding class."""
        raise NotImplementedError

    def check_permissions_patch(self, *args, **kwargs):
        """Function to check permissions, must be set by implementer"""
        raise NotImplementedError

    def patch(self, *args, **kwargs):
        """Handle PATCH request"""
        current_user = self._get_current_user()
        if not current_user:
            return {}, 403

        if not self.check_permissions_patch(*args, current_user=current_user, **kwargs):
            return {}, 404

        return self._patch(*args, current_user=current_user, **kwargs)

    def _put(self, *args, **kwargs):
        """Handle PUT request method to re-implemented by overriding class."""
        raise NotImplementedError

    def check_permissions_put(self, *args, **kwargs):
        """Function to check permissions, must be set by implementer"""
        raise NotImplementedError

    def put(self, *args, **kwargs):
        """Handle PUT request"""
        current_user = self._get_current_user()
        if not current_user:
            return {}, 403

        if not self.check_permissions_put(*args, current_user=current_user, **kwargs):
            return {}, 404

        return self._put(*args, current_user=current_user, **kwargs)

    def _delete(self, *args, **kwargs):
        """Handle DELETE request method to re-implemented by overriding class."""
        raise NotImplementedError

    def check_permissions_delete(self, *args, **kwargs):
        """Function to check permissions, must be set by implementer"""
        raise NotImplementedError

    def delete(self, *args, **kwargs):
        """Handle PUT request"""
        current_user = self._get_current_user()
        if not current_user:
            return {}, 403

        if not self.check_permissions_delete(*args, current_user=current_user, **kwargs):
            return {}, 404

        return self._delete(*args, current_user=current_user, **kwargs)


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
        return {"data": token.get_creation_api_details()}


class ApiTerraformUserTokens(AuthenticatedEndpoint):
    """Get user tokens for user"""

    def check_permissions_get(self, user_id, current_user, *args, **kwargs):
        """Check if user has permission to modify user tokens"""
        target_user = User.get_by_api_id(user_id)
        # @TODO Do not return 403 when user does not exist
        if not target_user:
            return False
        return UserPermissions(current_user=current_user, user=target_user).check_permission(
            UserPermissions.Permissions.CAN_MANAGE_USER_TOKENS)

    def _get(self, user_id, current_user):
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

    def check_permissions_post(self, current_user, user_id, *args, **kwargs):
        """Check if user has permission to modify user tokens"""
        target_user = User.get_by_api_id(user_id)
        # @TODO Do not return 403 when user does not exist
        if not target_user:
            return False
        return UserPermissions(current_user=current_user, user=target_user).check_permission(
            UserPermissions.Permissions.CAN_MANAGE_USER_TOKENS)

    def _post(self, current_user, user_id):
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


class ApiTerraformUserDetails(AuthenticatedEndpoint):
    """Interface to obtain user details"""

    def check_permissions_get(self, user_id, current_user):
        """Check permissions"""
        user = User.get_by_api_id(user_id)
        if not user:
            return False
        # @TODO check if users are part of a common organisation
        return True

    def _get(self, user_id, current_user):
        """Obtain user details"""
        user = User.get_by_api_id(user_id)
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

    def check_permissions_get(self, current_user):
        """Check permissions to access account details."""
        # All users can view their own account details
        return True

    def _get(self, current_user):
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

    def _get(self, current_user):
        """Obtain list of organisations"""
        return {
            'data': [
                organisation.get_api_details(effective_user=current_user)
                for organisation in current_user.organisations
            ]
        }

    def check_permissions_post(self, current_user):
        """Check permissions"""
        return UserPermissions(current_user=current_user, user=current_user).check_permission(
            UserPermissions.Permissions.CAN_CREATE_ORGANISATIONS)

    def _post(self, current_user):
        """Create new organisation"""
        json_data = flask.request.get_json().get('data', {})
        if json_data.get('type', None) != "organizations":
            return {}, 400

        attributes = json_data.get('attributes', {})
        name = attributes.get('name', None)
        email = attributes.get('email', None)

        if not email or not email:
            return {}, 400

        organisation = Organisation.create(name=name, email=email)

        if organisation is None:
            return {}, 400

        return {
            "data": organisation.get_api_details(effective_user=current_user)
        }


class ApiTerraformOrganisationDetails(AuthenticatedEndpoint):
    """Organisation details endpoint"""

    def check_permissions_get(self, organisation_name, current_user, *args, **kwargs):
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return False
        return OrganisationPermissions(organisation=organisation, current_user=current_user).check_permission(
            OrganisationPermissions.Permissions.CAN_ACCESS_VIA_TEAMS)

    def _get(self, current_user, organisation_name):
        """Get organisation details"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return {}, 404

        return {"data": organisation.get_api_details(effective_user=current_user)}

    def check_permissions_patch(self, organisation_name, current_user, *args, **kwargs):
        """Check permissions for updating organsation"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return False
        return OrganisationPermissions(organisation=organisation, current_user=current_user).check_permission(
            OrganisationPermissions.Permissions.CAN_UPDATE)

    def _patch(self, current_user, organisation_name):
        """Get organisation details"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return {}, 404

        json_data = flask.request.get_json().get('data', {})
        if json_data.get('type', None) != "organizations":
            return {}, 400

        attributes = json_data.get('attributes', {})
        name = attributes.get('name', None)
        email = attributes.get('email', None)

        if not email or not email:
            return {}, 400

        if not organisation.update_attributes(name=name, email=email):
            return {}, 400
        return {"data": organisation.get_api_details(effective_user=current_user)}



class ApiTerraformOrganisationEntitlementSet(AuthenticatedEndpoint):
    """Organisation entitlement endpoint."""

    def check_permissions_get(self, organisation_name, current_user, *args, **kwargs):
        """Check permissions"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return False
        return OrganisationPermissions(organisation=organisation, current_user=current_user).check_permission(
            OrganisationPermissions.Permissions.CAN_ACCESS_VIA_TEAMS)

    def _get(self, current_user, organisation_name):
        """Return entitlement-set for organisation"""
        organisation = Organisation.get_by_name_id(organisation_name)
        return organisation.get_entitlement_set_api()


class ApiTerraformOrganisationWorkspaces(AuthenticatedEndpoint):
    """Interface to list/create organisation workspaces"""

    def check_permissions_get(self, organisation_name, current_user, *args, **kwargs):
        """Check permissions"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return False
        return OrganisationPermissions(organisation=organisation, current_user=current_user).check_permission(
            OrganisationPermissions.Permissions.CAN_ACCESS_VIA_TEAMS)

    def _get(self, organisation_name, current_user):
        """Return list of workspaces for organisation"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return {}, 404

        return {
            "data": [
                workspace.get_api_details(effective_user=current_user)
                for workspace in organisation.workspaces
            ]
        }

    def check_permissions_post(self, organisation_name, current_user, *args, **kwargs):
        """Check permissions"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            print('NOT ORG FOND')
            return False
        return OrganisationPermissions(organisation=organisation, current_user=current_user).check_permission(
            OrganisationPermissions.Permissions.CAN_CREATE_WORKSPACE)

    def _post(self, organisation_name, current_user):
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
            "data": workspace.get_api_details(effective_user=current_user)
        }


class ApiTerraformOrganisationTasks(AuthenticatedEndpoint):
    """Interface to interact with organisation tasks."""

    def check_permissions_get(self, organisation_name, current_user, *args, **kwargs):
        """Check permissions"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return False
        return OrganisationPermissions(organisation=organisation, current_user=current_user).check_permission(
            OrganisationPermissions.Permissions.CAN_ACCESS_VIA_TEAMS)

    def _get(self, organisation_name, current_user):
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

    def check_permissions_post(self, organisation_name, current_user, *args, **kwargs):
        """Check permissions"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            print('NOT ORG FOND')
            return False
        return OrganisationPermissions(organisation=organisation, current_user=current_user).check_permission(
            OrganisationPermissions.Permissions.CAN_MANAGE_RUN_TASKS)

    def _post(self, organisation_name, current_user):
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


class ApiTerraformTaskDetails(AuthenticatedEndpoint):
    """Interface to view/edit a task"""

    def check_permissions_patch(self, task_id, current_user):
        """Check permissions"""
        task = Task.get_by_api_id(task_id)
        if not task:
            return False
        return OrganisationPermissions(
                organisation=task.organisation,
                current_user=current_user).check_permission(
            OrganisationPermissions.Permissions.CAN_MANAGE_RUN_TASKS)

    def _patch(self, task_id, current_user):
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

    def check_permissions_get(self, organisation_name, workspace_name, current_user, *args, **kwargs):
        """Check permissions"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return False
        workspace = Workspace.get_by_organisation_and_name(organisation, workspace_name)
        if not workspace:
            return False
        return WorkspacePermissions(current_user=current_user, workspace=workspace).check_permission(
            WorkspacePermissions.Permissions.CAN_READ_SETTINGS)

    def _get(self, organisation_name, workspace_name, current_user):
        """Return workspace details."""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return {}, 404
        workspace = Workspace.get_by_organisation_and_name(organisation, workspace_name)
        if not workspace:
            return {}, 404
        return {"data": workspace.get_api_details(effective_user=current_user)}


class ApiTerraformWorkspaceConfigurationVersions(AuthenticatedEndpoint):
    """Workspace configuration version interface"""

    def check_permissions_post(self, workspace_id, current_user, *args, **kwargs):
        """Check permissions"""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return False
        # As per documentation:
        # You need read runs permission to list and view configuration versions for a workspace, and you need queue plans permission to create new configuration versions.
        return WorkspacePermissions(current_user=current_user,
                                    workspace=workspace).check_access_type(
                                        runs=TeamWorkspaceRunsPermission.PLAN)

    def _post(self, workspace_id, current_user):
        """Create configuration version"""
        data = flask.request.get_json().get('data', {})
        attributes = data.get('attributes', {})

        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return {}, 404

        cv = ConfigurationVersion.create(
            workspace=workspace,
            auto_queue_runs=attributes.get('auto-queue-runs', True),
            speculative=attributes.get('speculative', False)
        )
        return cv.get_api_details()


class ApiTerraformWorkspaceRelationshipsTags(AuthenticatedEndpoint):
    """Interface to manage workspace tags"""

    def check_permissions_post(self, workspace_id, current_user):
        workspace = Workspace.get_by_api_id(workspace_id)
        if workspace is None:
            return False
        return WorkspacePermissions(
            current_user=current_user, workspace=workspace).check_permission(
            WorkspacePermissions.Permissions.CAN_MANAGE_TAGS)

    def _post(self, current_user, workspace_id):
        """Handle updating workspace tags"""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return 404

        request_data = request.json
        print(request_data)
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


class ApiTerraformConfigurationVersions(AuthenticatedEndpoint):
    """Workspace configuration version interface"""

    def check_permissions_get(self, current_user, configuration_version_id):
        """Check permissions"""
        cv = ConfigurationVersion.get_by_api_id(configuration_version_id)
        if not cv:
            return False
        return WorkspacePermissions(current_user=current_user,
                                    workspace=cv.workspace).check_access_type(
                                        runs=TeamWorkspaceRunsPermission.READ)

    def _get(self, configuration_version_id, current_user):
        """Get configuration version details."""
        cv = ConfigurationVersion.get_by_api_id(configuration_version_id)
        if not cv:
            return {}, 404
        return cv.get_api_details()


class ApiTerraformConfigurationVersionUpload(AuthenticatedEndpoint):
    """Configuration version upload endpoint"""

    def check_permissions_put(self, current_user, configuration_version_id):
        """Check permissions"""
        cv = ConfigurationVersion.get_by_api_id(configuration_version_id)
        if not cv:
            return False
        return WorkspacePermissions(current_user=current_user,
                                    workspace=cv.workspace).check_access_type(
                                        runs=TeamWorkspaceRunsPermission.PLAN)

    def _put(self, configuration_version_id, current_user):
        """Handle upload of configuration version data."""
        cv = ConfigurationVersion.get_by_api_id(configuration_version_id)
        if not cv:
            return {}, 404

        cv.process_upload(request.data)


class ApiTerraformRunConfigurationVersionDownload(AuthenticatedEndpoint):
    """Interface to download configuration version"""

    def check_permissions_get(self, current_user, run_id):
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

    def _get(self, current_user, run_id):
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

    def check_permissions_get(self, current_user, run_id=None,):
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

    def _get(self, current_user, run_id=None):
        """Return run information"""
        if not run_id:
            return {}, 404
        run = Run.get_by_api_id(run_id)
        if not run:
            return {}, 404
        return {"data": run.get_api_details()}

    def check_permissions_post(self, current_user, run_id=None,):
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

    def _post(self, current_user, run_id=None):
        """Create a run."""

        if run_id:
            return {}, 422

        print("CREATE RUN JSON")
        print(flask.request.get_json())

        data = flask.request.get_json().get('data', {})
        request_attributes = data.get('attributes', {})

        workspace_id = data.get('relationships', {}).get('workspace', {}).get('data', {}).get('id', None)
        if not workspace_id:
            return {}, 422

        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return {}, 404


        configuration_version_id = data.get('relationships', {}).get('configuration-version', {}).get('data', {}).get('id', None)
        if not configuration_version_id:
            return {}, 422

        cv = ConfigurationVersion.get_by_api_id(configuration_version_id)
        if not cv:
            return {}, 404

        if cv.workspace.id != workspace.id:
            print('Configuration version ID and workspace ID mismatch')
            # Hide error to prevent workspace ID/configuration ID enumeration
            return {}, 404

        create_attributes = {
            'auto_apply': request_attributes.get('auto-apply', workspace.auto_apply),
            'is_destroy': request_attributes.get('is-destroy', False),
            'message': request_attributes.get('message', "Queued manually via the Terraform Enterprise API"),
            'refresh': request_attributes.get('refresh', True),
            'refresh_only': request_attributes.get('refresh-only', False),
            'replace_addrs': request_attributes.get('replace-addrs'),
            'target_addrs': request_attributes.get('target-addrs'),
            'variables': request_attributes.get('variables', []),
            'plan_only': request_attributes.get('plan-only', cv.plan_only),
            'terraform_version': request_attributes.get('terraform-version'),
            'allow_empty_apply': request_attributes.get('allow-empty-apply')
        }

        run = Run.create(configuration_version=cv, created_by=current_user, **create_attributes)
        return {"data": run.get_api_details()}


class ApiTerraformRunAuditEvents(AuthenticatedEndpoint):
    """Interface to obtain audit events for run"""

    def check_permissions_get(self, current_user, run_id):
        """Check permissions"""
        run = Run.get_by_api_id(run_id)
        if not workspace:
            return False

        return WorkspacePermissions(
            current_user=current_user,
            workspace=run.configuration_version.workspace.organisation
        ).check_access_type(runs=TeamWorkspaceRunsPermission.READ)

    def _get(self, run_id, current_user):
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

    def check_permissions_post(self, run_id, current_user):
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

    def _post(self, run_id, current_user):
        """Cancel run"""
        run = Run.get_by_api_id(run_id)
        if not run:
            return {}, 404

        run.cancel(user=current_user)


class ApiTerraformWorkspaceRuns(AuthenticatedEndpoint):
    """Interface to obtain workspace runs,"""

    def check_permissions_get(self, current_user, workspace_id):
        """Check permissions"""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return False

        return WorkspacePermissions(
            current_user=current_user,
            workspace=workspace
        ).check_access_type(runs=TeamWorkspaceRunsPermission.READ)

    def _get(self, workspace_id, current_user):
        """Return all runs for a workspace."""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return {}, 404

        return {"data": [run.get_api_details() for run in workspace.runs]}


class ApiTerraformOrganisationQueue(AuthenticatedEndpoint):
    """Interface to obtain run queue for organisation"""

    def check_permissions_get(self, current_user, organisation_name):
        """Check permissions"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return {}, 404

        # @TODO Check this permission
        return OrganisationPermissions(
            current_user=current_user,
            organisation=organisation
        ).check_permission(OrganisationPermissions.Permissions.CAN_ACCESS_VIA_TEAMS)

    def _get(self, organisation_name, current_user):
        """Get list of runs queued"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return {}, 404

        return {"data": [run.get_api_details() for run in organisation.get_run_queue()]}


class ApiTerraformPlans(AuthenticatedEndpoint):
    """Interface for plans."""

    def check_permissions_get(self, current_user, plan_id=None):
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

    def _get(self, current_user, plan_id=None):
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
            print('Waiting as plan state is; ' + str(plan.status))

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

    def check_permissions_get(self, current_user, workspace_id):
        """Check permissions to view run"""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return False

        return WorkspacePermissions(
            current_user=current_user,
            workspace=workspace
        ).check_access_type(state_versions=TeamWorkspaceStateVersionsPermissions.READ)

    def _get(self, current_user, workspace_id):
        """Return latest state for workspace."""

        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return {}, 404

        state = Workspace.get_by_api_id(workspace_id).latest_state
        if not state:
            return {}, 404
        
        return {'data': state.get_api_details()}


class ApiTerraformStateVersionDownload(AuthenticatedEndpoint):

    def check_permissions_get(self, current_user, state_version_id):
        """Check permissions to view run"""
        state_version = StateVersion.get_by_api_id(state_version_id)
        if not state_version_id:
            return False

        return WorkspacePermissions(
            current_user=current_user,
            workspace=state_version.workspace
        ).check_access_type(state_versions=TeamWorkspaceStateVersionsPermissions.READ)

    def _get(self, current_user, state_version_id):
        """Return state version json"""
        state_version = StateVersion.get_by_api_id(state_version_id)
        if not state_version_id:
            return {}, 404
        return json.loads(state_version._state_json)


class ApiTerraformApplyRun(AuthenticatedEndpoint):
    """Interface to confirm run"""

    def check_permissions_post(self, current_user, run_id):
        """Check permissions to view run"""
        run = Run.get_by_api_id(run_id)
        if not run:
            return False

        return WorkspacePermissions(
            current_user=current_user,
            workspace=run.configuration_version.workspace
        ).check_access_type(runs=TeamWorkspaceRunsPermission.APPLY)

    def _post(self, current_user, run_id):
        """Initialise run apply."""
        run = Run.get_by_api_id(run_id)
        if not run:
            return {}, 404
        Apply.create(plan=run.plan)
        run.queue_apply(comment=flask.request.get_json().get('comment', None), user=current_user)
        return {}, 202


class ApiTerraformApplies(AuthenticatedEndpoint):
    """Interface for applies"""

    def check_permissions_get(self, current_user, apply_id=None):
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

    def _get(self, current_user, apply_id=None):
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
            print('Waiting as apply state is; ' + str(apply.status))

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

    def check_permissions_post(self, current_user):
        """Check permissions"""
        return UserPermissions(current_user=current_user, user=current_user).check_permission(
            UserPermissions.Permissions.CAN_CREATE_ORGANISATIONS)

    def _post(self, current_user):
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


class ApiTerrarunWorkspaceCreateNameValidation(AuthenticatedEndpoint):
    """Endpoint to validate new workspace name"""

    def check_permissions_post(self, organisation_name, current_user):
        """Check permissions"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return False
        return OrganisationPermissions(current_user=current_user, organisation=organisation).check_permission(
            OrganisationPermissions.Permissions.CAN_CREATE_WORKSPACE)

    def _post(self, organisation_name, current_user):
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
    """Endpoint to validate new workspace name"""

    def check_permissions_post(self, organisation_name, current_user):
        """Check permissions"""
        organisation = Organisation.get_by_name_id(organisation_name)
        if not organisation:
            return False
        return OrganisationPermissions(current_user=current_user, organisation=organisation).check_permission(
            OrganisationPermissions.Permissions.CAN_MANAGE_RUN_TASKS)

    def _post(self, organisation_name, current_user):
        """Validate new organisation name"""
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


class ApiTerraformWorkspaceTasks(AuthenticatedEndpoint):
    """Interface to manage workspace tasks"""

    def check_permissions_get(self, workspace_id, current_user):
        """Check permissions"""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return False
        return WorkspacePermissions(
            current_user=current_user, workspace=workspace
        ).check_permission(WorkspacePermissions.Permissions.CAN_READ_SETTINGS)

    def _get(self, workspace_id, current_user):
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

    def check_permissions_post(self, workspace_id, current_user):
        """Check permissions"""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return False
        return WorkspacePermissions(
            current_user=current_user, workspace=workspace
        ).check_permission(WorkspacePermissions.Permissions.CAN_MANAGE_RUN_TASKS)

    def _post(self, workspace_id, current_user):
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

    def check_permissions_get(self, workspace_id, workspace_task_id, current_user):
        """Check permissions"""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return False
        return WorkspacePermissions(
            current_user=current_user, workspace=workspace
        ).check_permission(WorkspacePermissions.Permissions.CAN_READ_SETTINGS)

    def _get(self, workspace_id, workspace_task_id, current_user):
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

    def check_permissions_delete(self, workspace_id, workspace_task_id, current_user):
        """Check permissions"""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return False
        return WorkspacePermissions(
            current_user=current_user, workspace=workspace
        ).check_permission(WorkspacePermissions.Permissions.CAN_MANAGE_RUN_TASKS)

    def _delete(self, workspace_id, workspace_task_id, current_user):
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
