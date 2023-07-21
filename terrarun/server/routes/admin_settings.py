

from flask import request

from terrarun.api_request import ApiRequest
from terrarun.permissions.user import UserPermissions
from terrarun.saml import Saml
from terrarun.server.route_registration import RouteRegistration
from terrarun.server.authenticated_endpoint import AuthenticatedEndpoint


class AdminSettingsSamlSettings(AuthenticatedEndpoint):

    def check_permissions_get(self, current_user, current_job):
        """Check permissions to view SAML settings"""
        return current_user.site_admin

    def _get(self, current_user, current_job):
        """Obtain SAML settings"""
        saml = Saml()
        api_request = ApiRequest(request)
        api_request.set_data(saml.get_api_details())
        return api_request.get_response()


class AdminSettingsRouteRegistration(RouteRegistration):
    """Register admin settings routes"""

    def register_routes(self, app, api):
        """Register routes"""
        api.add_resource(
            AdminSettingsSamlSettings,
            "/api/v2/admin/saml-settings"
        )
