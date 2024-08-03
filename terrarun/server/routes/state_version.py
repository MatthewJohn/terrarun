# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

from typing import Optional

from flask import request
import flask
import flask_restful

import terrarun.auth_context
from terrarun.api_entities.state_version import (
    StateVersionView
)
import terrarun.models.run_queue
import terrarun.models.user
from terrarun.server.authenticated_endpoint import AuthenticatedEndpoint
from terrarun.server.route_registration import RouteRegistration
from terrarun.models.team_workspace_access import TeamWorkspaceStateVersionsPermissions
from terrarun.models.workspace import WorkspacePermissions
from terrarun.models.state_version import StateVersion


class AdminTerraformVersionsRegistration(RouteRegistration):
    """Register admin settings routes"""

    def register_routes(self, app: 'flask.app', api: 'flask_restful.Api'):
        """Register routes"""
        api.add_resource(
            ApiTerraformStateVersion,
            '/api/v2/state-versions/<string:state_version_id>'
        )
        api.add_resource(
            ApiTerraformStateVersionDownload,
            '/api/v2/state-versions/<string:state_version_id>/download'
        )


class ApiTerraformStateVersion(AuthenticatedEndpoint):

    def check_permissions_get(self, auth_context: 'terrarun.auth_context.AuthContext', state_version_id: int):
        """Check permissions to read state versions"""
        state_version = StateVersion.get_by_api_id(state_version_id)
        if not state_version:
            return False

        if auth_context.job and auth_context.job.run.configuration_version.workspace == state_version.workspace:
            return True

        return WorkspacePermissions(
            current_user=auth_context.user,
            workspace=state_version.workspace
        ).check_access_type(state_versions=TeamWorkspaceStateVersionsPermissions.READ)

    def _get(self, auth_context: 'terrarun.auth_context.AuthContext', state_version_id: int):
        """Return state version json"""
        state_version = StateVersion.get_by_api_id(state_version_id)
        if not state_version:
            return {}, 404

        view = StateVersionView.from_object(obj=state_version, effective_user=auth_context.user)
        return view.to_response()


class ApiTerraformStateVersionDownload(AuthenticatedEndpoint):

    def check_permissions_get(self, auth_context: 'terrarun.auth_context.AuthContext', state_version_id: int):
        """Check permissions to read state versions"""
        state_version = StateVersion.get_by_api_id(state_version_id)
        if not state_version:
            return False

        if auth_context.job and auth_context.job.run.configuration_version.workspace == state_version.workspace:
            return True

        return WorkspacePermissions(
            current_user=auth_context.user,
            workspace=state_version.workspace
        ).check_access_type(state_versions=TeamWorkspaceStateVersionsPermissions.READ)

    def _get(self, auth_context: 'terrarun.auth_context.AuthContext', state_version_id: int):
        """Return state version json"""
        state_version = StateVersion.get_by_api_id(state_version_id)
        if not state_version:
            return {}, 404
        return state_version.state
