# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

import json
from typing import Optional

import flask
import flask_restful
from flask import request

import terrarun.models.run_queue
import terrarun.models.user
import terrarun.auth_context
from terrarun.errors import ApiError
from terrarun.api_entities.state_version import (
    StateVersionView
)
from terrarun.server.authenticated_endpoint import AuthenticatedEndpoint
from terrarun.server.signature_authenticated_endpoint import SignatureAuthenticatedEndpoint
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
            ApiTerraformStateVersionDownloadState,
            '/api/v2/state-versions/<string:state_version_id>/download'
        )
        api.add_resource(
            ApiTerraformStateVersionDownloadJsonState,
            '/api/v2/state-versions/<string:state_version_id>/json-download'
        )
        api.add_resource(
            ApiTerraformStateVersionUploadState,
            '/api/v2/state-versions/<string:state_version_id>/upload'
        )
        api.add_resource(
            ApiTerraformStateVersionUploadJsonState,
            '/api/v2/state-versions/<string:state_version_id>/json-upload'
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

        view = StateVersionView.from_object(obj=state_version, auth_context=auth_context)
        return view.to_response()


class ApiTerraformStateVersionUploadState(SignatureAuthenticatedEndpoint):

    def check_permissions_put(self, auth_context: 'terrarun.auth_context.AuthContext', state_version_id: int):
        """Check permissions to read state versions"""
        state_version = StateVersion.get_by_api_id(state_version_id)
        if not state_version:
            return False

        if auth_context.job and auth_context.job.run.configuration_version.workspace == state_version.workspace:
            return True

        return WorkspacePermissions(
            current_user=auth_context.user,
            workspace=state_version.workspace
        ).check_access_type(state_versions=TeamWorkspaceStateVersionsPermissions.WRITE)

    def _put(self, auth_context: 'terrarun.auth_context.AuthContext', state_version_id: int):
        """Return state version json"""
        state_version = StateVersion.get_by_api_id(state_version_id)
        if not state_version:
            return {}, 404

        # Validate request data as valid JSON
        try:
            data = json.loads(request.data)
        except:
            raise ApiError(
                "Invalid payload",
                "JSON payload is invalid.",
            )

        if not state_version.handle_state_upload(data, auth_context=auth_context):
            return {}, 400

        return {}, 200


class ApiTerraformStateVersionUploadJsonState(SignatureAuthenticatedEndpoint):

    def check_permissions_put(self, auth_context: 'terrarun.auth_context.AuthContext', state_version_id: int):
        """Check permissions to read state versions"""
        state_version = StateVersion.get_by_api_id(state_version_id)
        if not state_version:
            return False

        if auth_context.job and auth_context.job.run.configuration_version.workspace == state_version.workspace:
            return True

        return WorkspacePermissions(
            current_user=auth_context.user,
            workspace=state_version.workspace
        ).check_access_type(state_versions=TeamWorkspaceStateVersionsPermissions.WRITE)

    def _put(self, auth_context: 'terrarun.auth_context.AuthContext', state_version_id: int):
        """Return state version json"""
        state_version = StateVersion.get_by_api_id(state_version_id)
        if not state_version:
            return {}, 404

        # Validate request data as valid JSON
        try:
            data = json.loads(request.data)
        except:
            raise ApiError(
                "Invalid payload",
                "JSON payload is invalid.",
            )

        if not state_version.handle_json_state_upload(data, auth_context=auth_context):
            return {}, 400

        return {}, 200


class ApiTerraformStateVersionDownloadState(SignatureAuthenticatedEndpoint):

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


class ApiTerraformStateVersionDownloadJsonState(SignatureAuthenticatedEndpoint):

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

        return state_version.json_state
