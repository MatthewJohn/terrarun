
from flask import Flask, make_response
from flask_restful import Api, Resource

from terrarun.auth import Auth


class Server(object):
    """Manage web server and route requests"""

    def __init__(self, ssl_public_key=None, ssl_private_key=None):
        """Create flask app and store member variables"""
        self._app = Flask(
            __name__,
            static_folder='static',
            template_folder='templates'
        )
        self._api = Api(
            self._app,
        )

        self.host = '0.0.0.0'
        self.port = 5002
        self.ssl_public_key = ssl_public_key
        self.ssl_private_key = ssl_private_key

        self._register_routes()

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

        # Views
        self._app.route('/app/settings/tokens')(self._view_serve_settings_tokens)

    def _view_serve_settings_tokens(self):
        """Return authentication tokens"""
        return Auth().get_auth_token()

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

        self._app.run(**kwargs)


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


class ApiTerraformMotd(Resource):
    """Return MOTD for terraform"""

    def get(self):
        """Return MOTD message."""
        return {
            'msg': 'This is a test Terrarun server\nNo functionality yet.'
        }
