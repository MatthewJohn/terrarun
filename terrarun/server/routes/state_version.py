# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0


from flask import request

from terrarun.server.authenticated_endpoint import AuthenticatedEndpoint
from terrarun.server.route_registration import RouteRegistration
from terrarun.models.team_workspace_access import TeamWorkspaceStateVersionsPermissions
from terrarun.models.workspace import WorkspacePermissions
from terrarun.models.state_version import StateVersion


class AdminTerraformVersionsRegistration(RouteRegistration):
    """Register admin settings routes"""

    def register_routes(self, app, api):
        """Register routes"""
        api.add_resource(
            ApiTerraformStateVersionDownload,
            '/api/v2/state-versions/<string:state_version_id>/download'
        )

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