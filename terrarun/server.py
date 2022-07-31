
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

from terrarun.apply import Apply
from terrarun.configuration import ConfigurationVersion
from terrarun.database import Database
from terrarun.organisation import Organisation
from terrarun.plan import Plan
from terrarun.run import Run
from terrarun.run_queue import RunQueue
from terrarun.state_version import StateVersion
from terrarun.terraform_command import TerraformCommandState
from terrarun.user_token import UserToken, UserTokenType
from terrarun.workspace import Workspace
from terrarun.user import User


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
            ApiTerraformOrganisationEntitlementSet,
            '/api/v2/organizations/<string:organisation_name>/entitlement-set'
        )
        self._api.add_resource(
            ApiTerraformWorkspace,
            '/api/v2/organizations/<string:organisation_name>/workspaces/<string:workspace_name>'
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
            ApiTerraformConfigurationVersionUpload,
            '/api/v2/upload-configuration/<string:configuration_version_id>'
        )
        self._api.add_resource(
            ApiTerraformConfigurationVersions,
            '/api/v2/configuration-versions/<string:configuration_version_id>'
        )
        self._api.add_resource(
            ApiTerraformRun,
            '/api/v2/runs',
            '/api/v2/runs/<string:run_id>'
        )
        self._api.add_resource(
            ApiTerraformWorkspaceRuns,
            '/api/v2/workspaces/<string:workspace_id>/runs'
        )
        self._api.add_resource(
            ApiTerraformOrganisationQueue,
            '/api/v2/organizations/<string:organisation_name>/runs/queue'
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
            ApiTerraformUserTokens,
            '/api/v2/users/<string:user_id>/authentication-tokens'
        )

        # Custom endpoints
        self._api.add_resource(
            ApiAuthenticate,
            '/api/terrarun/v1/authenticate'
        )

    def run(self, debug=None):
        """Run flask server."""
        kwargs = {
            'host': self.host,
            'port': self.port,
            'debug': True
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


class ApiTerraformUserTokens(Resource):
    """Get user tokens for user"""

    def get(self, user_id):
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
    
    def post(self, user_id):
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
        return response


class ApiTerraformAccountDetails(Resource):
    """Interface to obtain current account"""

    def get(self):
        """Get current account details"""
        authorization_header = request.headers.get('Authorization', '')
        auth_token = re.sub(r'^Bearer ', '', authorization_header)
        user_token = UserToken.get_by_token(auth_token)
        if not user_token:
            return {}, 403
        return user_token.user.get_api_details()


class ApiTerraformMotd(Resource):
    """Return MOTD for terraform"""

    def get(self):
        """Return MOTD message."""
        return {
            'msg': 'This is a test Terrarun server\nNo functionality yet.'
        }


class ApiTerraformOrganisationEntitlementSet(Resource):
    """Organisation entitlement endpoint."""

    def get(self, organisation_name):
        """Return entitlement-set for organisation"""
        organisation = Organisation.get_by_name(organisation_name)
        return organisation.get_entitlement_set_api()


class ApiTerraformWorkspace(Resource):
    """Organisation workspace details endpoint."""

    def get(self, organisation_name, workspace_name):
        """Return workspace details."""
        organisation = Organisation.get_by_name(organisation_name)
        workspace = Workspace.get_by_organisation_and_name(organisation, workspace_name)
        return workspace.get_api_details()


class ApiTerraformWorkspaceConfigurationVersions(Resource):
    """Workspace configuration version interface"""

    def post(self, workspace_id):
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


class ApiTerraformConfigurationVersions(Resource):
    """Workspace configuration version interface"""

    def get(self, configuration_version_id):
        """Get configuration version details."""
        cv = ConfigurationVersion.get_by_api_id(configuration_version_id)
        if not cv:
            return {}, 404
        return cv.get_api_details()


class ApiTerraformConfigurationVersionUpload(Resource):
    """Configuration version upload endpoint"""

    def put(self, configuration_version_id):
        """Handle upload of configuration version data."""
        cv = ConfigurationVersion.get_by_api_id(configuration_version_id)
        if not cv:
            return {}, 404

        cv.process_upload(request.data)


class ApiTerraformRun(Resource):
    """Run interface."""

    def get(self, run_id=None):
        """Return run information"""
        run = Run.get_by_api_id(run_id)
        if not run:
            return {}, 404
        return {"data": run.get_api_details()}

    def post(self, run_id=None):
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

        run = Run.create(cv, **create_attributes)
        return {"data": run.get_api_details()}


class ApiTerraformWorkspaceRuns(Resource):
    """Interface to obtain workspace runs,"""

    def get(self, workspace_id):
        """Return all runs for a workspace."""
        workspace = Workspace.get_by_api_id(workspace_id)
        if not workspace:
            return {}, 404

        return {"data": [run.get_api_details() for run in workspace.runs]}


class ApiTerraformOrganisationQueue(Resource):
    """Interface to obtain run queue for organisation"""

    def get(self, organisation_name):
        """Get list of runs queued"""
        organisation = Organisation.get_by_name(organisation_name)
        if not organisation:
            return {}, 404

        return {"data": [run.get_api_details() for run in organisation.get_run_queue()]}


class ApiTerraformPlans(Resource):
    """Interface for plans."""

    def get(self, plan_id=None):
        """Return information for plan(s)"""
        if plan_id:
            plan = Plan.get_by_api_id(plan_id)
            if not plan:
                return {}, 404

            return {"data": plan.get_api_details()}

        raise Exception('Need to return list of plans?')


class ApiTerraformPlanLog(Resource):
    """Interface to obtain logs from stream."""

    def get(self, plan_id):
        """Return information for plan(s)"""

        parser = reqparse.RequestParser()
        parser.add_argument('offset', type=int, location='args')
        parser.add_argument('limit', type=int, location='args')
        args = parser.parse_args()
        plan = Plan.get_by_api_id(plan_id)
        if not plan:
            return {}, 404

        plan_output = b""
        session = Database.get_session()
        for _ in range(60):
            session.refresh(plan)
            if plan.log:
                session.refresh(plan.log)
                if plan.log.data:
                    plan_output = plan.log.data[args.offset:(args.offset+args.limit)]
            if plan_output or plan.status not in [
                    TerraformCommandState.PENDING,
                    TerraformCommandState.MANAGE_QUEUED,
                    TerraformCommandState.QUEUED,
                    TerraformCommandState.RUNNING]:
                break
            print('Waiting as plan state is; ' + str(plan.status))

            sleep(0.5)

        response = make_response(plan_output)
        response.headers['Content-Type'] = 'text/plain'
        return response


class ApiTerraformWorkspaceLatestStateVersion(Resource):

    def get(self, workspace_id):
        """Return latest state for workspace."""

        state = Workspace.get_by_api_id(workspace_id)._latest_state
        if state:
            return {'data': state.get_api_details()}

        return {}, 404


class ApiTerraformStateVersionDownload(Resource):

    def get(self, state_version_id):
        """Return state version json"""
        state_version = StateVersion.get_by_api_id(state_version_id)
        if not state_version_id:
            return {}, 404
        return state_version._state_json


class ApiTerraformApplyRun(Resource):
    """Interface to confirm run"""

    def post(self, run_id):
        """Initialise run apply."""
        run = Run.get_by_api_id(run_id)
        if not run:
            return {}, 404
        run.queue_apply(comment=flask.request.get_json().get('comment', None))
        return {}, 202


class ApiTerraformApplies(Resource):
    """Interface for applies"""

    def get(self, apply_id=None):
        """Get apply details."""
        if not apply_id:
            raise Exception('IT WAS CALLED')

        apply = Apply.get_by_api_id(apply_id)
        if not apply:
            return {}, 404
        
        return {'data': apply.get_api_details()}


class ApiTerraformApplyLog(Resource):
    """Interface to obtain logs from stream."""

    def get(self, apply_id):
        """Return information for plan(s)"""

        parser = reqparse.RequestParser()
        parser.add_argument('offset', type=int, location='args')
        parser.add_argument('limit', type=int, location='args')
        args = parser.parse_args()
        apply = Apply.get_by_api_id(apply_id)
        if not apply:
            return {}, 404

        output = b""
        session = Database.get_session()
        for _ in range(60):
            session.refresh(apply)
            if apply.log:
                session.refresh(apply.log)
                if apply.log.data:
                    output = apply.log.data[args.offset:(args.offset+args.limit)]
            if output or apply.status not in [
                    TerraformCommandState.PENDING,
                    TerraformCommandState.MANAGE_QUEUED,
                    TerraformCommandState.QUEUED,
                    TerraformCommandState.RUNNING]:
                break
            print('Waiting as apply state is; ' + str(apply.status))

            sleep(0.5)

        response = make_response(output)
        response.headers['Content-Type'] = 'text/plain'
        return response
