# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0



from flask import request
from terrarun.api_entities.base_entity import ApiErrorView
from terrarun.api_entities.saml_settings import SamlSettingsUpdateEntity, SamlSettingsView
from terrarun.api_error import ApiError

import terrarun.auth_context
from terrarun.api_request import ApiRequest
from terrarun.permissions.user import UserPermissions
from terrarun.models.saml_settings import SamlSettings
from terrarun.server.route_registration import RouteRegistration
from terrarun.server.authenticated_endpoint import AuthenticatedEndpoint


class AdminSettingsSamlSettings(AuthenticatedEndpoint):

    def check_permissions_get(self, auth_context: 'terrarun.auth_context.AuthContext'):
        """Check permissions to view SAML settings"""
        return auth_context.user and auth_context.user.site_admin

    def _get(self, auth_context: 'terrarun.auth_context.AuthContext'):
        """Obtain SAML settings"""
        saml_settings = SamlSettings.get_instance()
        view = SamlSettingsView.from_object(saml_settings, auth_context.user)
        return view.to_response()

    def check_permissions_post(self, auth_context: 'terrarun.auth_context.AuthContext'):
        """Check permissions to update SAML settings"""
        return auth_context.user and auth_context.user.site_admin

    def _post(self, auth_context: 'terrarun.auth_context.AuthContext'):
        """Update SAML settings"""
        saml_settings = SamlSettings.get_instance()

        err, update_entity = SamlSettingsUpdateEntity.from_request(request.json)
        if err:
            return ApiErrorView(error=err).to_response()

        try:
            saml_settings.update_attributes(update_entity)
        except ApiError as exc:
            return ApiErrorView(error=exc).to_response()

        view = SamlSettingsView.from_object(saml_settings, auth_context=auth_context)
        return view.to_response()



class AdminSettingsRouteRegistration(RouteRegistration):
    """Register admin settings routes"""

    def register_routes(self, app, api):
        """Register routes"""
        api.add_resource(
            AdminSettingsSamlSettings,
            "/api/v2/admin/saml-settings"
        )
