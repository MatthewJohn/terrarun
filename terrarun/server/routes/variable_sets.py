

from flask import request
from terrarun import api_error
from terrarun.api_entities.base_entity import ApiErrorView
from terrarun.api_entities.variable_set import VariableSetCreateEntity, VariableSetView
from terrarun.api_error import ApiError

from terrarun.api_request import ApiRequest
from terrarun.commands.variable_set import validate_new_variable_set
from terrarun.models.workspace import Workspace
from terrarun.permissions.user import UserPermissions
from terrarun.models.saml_settings import SamlSettings
from terrarun.server.route_registration import RouteRegistration
from terrarun.server.authenticated_endpoint import AuthenticatedEndpoint


class VariableSet(AuthenticatedEndpoint):


    def check_permissions_post(self, organisation_id, current_user, current_job):
        """Check permissions to create variable set in organisation"""
        # @TODO check organsation and 
        return current_user.site_admin

    def _post(self, organisation_id, current_user, current_job):
        """Update SAML settings"""

        err, create_entity = VariableSetCreateEntity.from_request(request.json)
        if err:
            return ApiErrorView(error=err).to_response()

        validate_new_variable_set(create_entity)

        variable_set = create_entity.to_object()

        create_entity.id = "abcdefg"

        view_entity = VariableSetView.from_object(variable_set)
        return create_entity.to_response()



class VariableSetsRouteRegistration(RouteRegistration):
    """Register variable set routes"""

    def register_routes(self, app, api):
        """Register routes"""
        api.add_resource(
            VariableSet,
            "/api/v2/organizations/<string:organisation_id>/varsets"
        )
