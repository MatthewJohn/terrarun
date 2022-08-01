
from enum import Enum

import terrarun.team_workspace_access


class WorkspacePermissions:
    """Provide interface to obtain and check permissions for user against workspace"""

    class Permissions(Enum):
        """List of permissions"""
        CAN_CREATE_STATE_VERSIONS = "can-create-state-versions"
        CAN_DESTROY = "can-destroy"
        CAN_FORCE_UNLOCK = "can-force-unlock"
        CAN_LOCK = "can-lock"
        CAN_MANAGE_RUN_TASKS = "can-manage-run-tasks"
        CAN_MANAGE_TAGS = "can-manage-tags"
        CAN_QUEUE_APPLY = "can-queue-apply"
        CAN_QUEUE_DESTROY = "can-queue-destroy"
        CAN_QUEUE_RUN = "can-queue-run"
        CAN_READ_ASSESSMENT_RESULT = "can-read-assessment-result"
        CAN_READ_SETTINGS = "can-read-settings"
        CAN_READ_STATE_VERSIONS = "can-read-state-versions"
        CAN_READ_VARIABLE = "can-read-variable"
        CAN_UNLOCK = "can-unlock"
        CAN_UPDATE = "can-update"
        CAN_UPDATE_VARIABLE = "can-update-variable"

    def __init__(self, current_user, workspace):
        """Store member variables"""
        self._current_user = current_user
        self._workspace = workspace

    def _check_team_permission(self, team_workspace_access, permission):
        """Check if team has a given permission."""
        if permission is self.Permissions.CAN_CREATE_STATE_VERSIONS:
            if (team_workspace_access.access_type in [
                    terrarun.team_workspace_access.TeamWorkspaceAccessType.WRITE,
                    terrarun.team_workspace_access.TeamWorkspaceAccessType.ADMIN] or
                    (team_workspace_access.access_type is terrarun.team_workspace_access.TeamWorkspaceAccessType.CUSTOM and
                     team_workspace_access.permission_state_versions in [terrarun.team_workspace_access.TeamWorkspaceStateVersionsPermissions.WRITE])):
                return True
        elif permission is self.Permissions.CAN_DESTROY:
            if (team_workspace_access.access_type in [
                    terrarun.team_workspace_access.TeamWorkspaceAccessType.WRITE,
                    terrarun.team_workspace_access.TeamWorkspaceAccessType.ADMIN] or
                    (team_workspace_access.access_type is terrarun.team_workspace_access.TeamWorkspaceAccessType.CUSTOM and
                     team_workspace_access.permission_runs in [terrarun.team_workspace_access.TeamWorkspaceRunsPermission.APPLY])):
                return True

    def check_permission(self, permission):
        """Check if user has single permission."""
        # If user is site admin, allow permission
        if self._current_user.site_admin:
            return True
        # If user is an organisation owner,
        # give all permissions
        if self._current_user.api_id in [owner.api_id for owner in self._workspace.organisation.owners]:
            return True

        user_teams = self._current_user.teams

        # Check team permissions
        for team in user_teams:
            # Iterate over all team workspace accesses for current team
            for team_workspace_access in team.workspace_accesses:
                # Check if team workspace access is for current workspace
                if team_workspace_access.workspace.id == self._workspace.id:
                    # Check workspace permissions
                    if self._check_team_permission(team_workspace_access=team_workspace_access, permission=permission):
                        return True

        return False

    def get_api_permissions(self):
        """Return list of permissions for API"""
        return {
            permission.value: self.check_permission(permission)
            for permission in self.Permissions
        }