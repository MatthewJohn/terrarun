# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

from enum import Enum

import terrarun.models.team_workspace_access


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
                    terrarun.models.team_workspace_access.TeamWorkspaceAccessType.WRITE,
                    terrarun.models.team_workspace_access.TeamWorkspaceAccessType.ADMIN] or
                    (team_workspace_access.access_type is terrarun.models.team_workspace_access.TeamWorkspaceAccessType.CUSTOM and
                     team_workspace_access.permission_state_versions in [terrarun.models.team_workspace_access.TeamWorkspaceStateVersionsPermissions.WRITE])):
                return True
        elif permission is self.Permissions.CAN_DESTROY:
            if (team_workspace_access.access_type in [
                    terrarun.models.team_workspace_access.TeamWorkspaceAccessType.WRITE,
                    terrarun.models.team_workspace_access.TeamWorkspaceAccessType.ADMIN] or
                    (team_workspace_access.access_type is terrarun.models.team_workspace_access.TeamWorkspaceAccessType.CUSTOM and
                     team_workspace_access.permission_runs in [terrarun.models.team_workspace_access.TeamWorkspaceRunsPermission.APPLY])):
                return True

    def check_permission(self, permission):
        """Check if user has single permission."""
        if not self._current_user:
            return False

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

    def _team_has_access_type(self, team_workspace_access, required_type):
        """Check if team has overall access type."""
        allowed_types = []
        # The documentation states the permissions in order:
        # read, plan, write, admin, custom, which implies the order of inheritance
        if required_type is terrarun.models.team_workspace_access.TeamWorkspaceAccessType.ADMIN:
            allowed_types = [terrarun.models.team_workspace_access.TeamWorkspaceAccessType.ADMIN]

        elif required_type is terrarun.models.team_workspace_access.TeamWorkspaceAccessType.WRITE:
            allowed_types = [terrarun.models.team_workspace_access.TeamWorkspaceAccessType.ADMIN,
                             terrarun.models.team_workspace_access.TeamWorkspaceAccessType.WRITE]

        elif required_type is terrarun.models.team_workspace_access.TeamWorkspaceAccessType.PLAN:
            allowed_types = [terrarun.models.team_workspace_access.TeamWorkspaceAccessType.ADMIN,
                             terrarun.models.team_workspace_access.TeamWorkspaceAccessType.WRITE,
                             terrarun.models.team_workspace_access.TeamWorkspaceAccessType.PLAN]

        elif required_type is terrarun.models.team_workspace_access.TeamWorkspaceAccessType.READ:
            allowed_types = [terrarun.models.team_workspace_access.TeamWorkspaceAccessType.ADMIN,
                             terrarun.models.team_workspace_access.TeamWorkspaceAccessType.WRITE,
                             terrarun.models.team_workspace_access.TeamWorkspaceAccessType.PLAN,
                             terrarun.models.team_workspace_access.TeamWorkspaceAccessType.READ]
        else:
            raise Exception('Invalid required_type for global workspace access')

        return team_workspace_access.access_type in allowed_types

    def _check_team_access_type(self, team_workspace_access, runs, variables,
                                state_versions, sentinel_mocks,
                                workspace_locking, run_tasks):
        """Check team access for a particualr access type."""
        # Check only one permission type is being assessed
        found_access_type = False
        for perm in [runs, variables, state_versions, sentinel_mocks, workspace_locking, run_tasks]:
            if perm is not None:
                if found_access_type:
                    raise Exception('Cannot check multiple access types in one call to check_access_type')
                found_access_type = True

        # Check runs permissions
        if runs is not None:
            if runs is terrarun.models.team_workspace_access.TeamWorkspaceRunsPermission.APPLY:
                return (self._team_has_access_type(team_workspace_access, terrarun.models.team_workspace_access.TeamWorkspaceAccessType.WRITE) or
                        (team_workspace_access.access_type is terrarun.models.team_workspace_access.TeamWorkspaceAccessType.CUSTOM and
                        team_workspace_access.permission_runs in [terrarun.models.team_workspace_access.TeamWorkspaceRunsPermission.APPLY]))

            elif runs is terrarun.models.team_workspace_access.TeamWorkspaceRunsPermission.PLAN:
                return (self._team_has_access_type(team_workspace_access, terrarun.models.team_workspace_access.TeamWorkspaceAccessType.PLAN) or
                        (team_workspace_access.access_type is terrarun.models.team_workspace_access.TeamWorkspaceAccessType.CUSTOM and
                         team_workspace_access.permission_runs in [terrarun.models.team_workspace_access.TeamWorkspaceRunsPermission.PLAN,
                                                                   terrarun.models.team_workspace_access.TeamWorkspaceRunsPermission.APPLY]))

            elif runs is terrarun.models.team_workspace_access.TeamWorkspaceRunsPermission.READ:
                return (self._team_has_access_type(team_workspace_access, terrarun.models.team_workspace_access.TeamWorkspaceAccessType.READ) or
                        (team_workspace_access.access_type is terrarun.models.team_workspace_access.TeamWorkspaceAccessType.CUSTOM and
                         team_workspace_access.permission_runs in [terrarun.models.team_workspace_access.TeamWorkspaceRunsPermission.READ,
                                                                   terrarun.models.team_workspace_access.TeamWorkspaceRunsPermission.PLAN,
                                                                   terrarun.models.team_workspace_access.TeamWorkspaceRunsPermission.APPLY]))

        # Check variables permissions
        elif variables is not None:
            if variables is terrarun.models.team_workspace_access.TeamWorkspaceVariablesPermission.WRITE:
                return (self._team_has_access_type(team_workspace_access, terrarun.models.team_workspace_access.TeamWorkspaceAccessType.WRITE) or
                        (team_workspace_access.access_type is terrarun.models.team_workspace_access.TeamWorkspaceAccessType.CUSTOM and
                         team_workspace_access.permission_variables in [terrarun.models.team_workspace_access.TeamWorkspaceVariablesPermission.WRITE]))

            elif variables is terrarun.models.team_workspace_access.TeamWorkspaceVariablesPermission.READ:
                return (self._team_has_access_type(team_workspace_access, terrarun.models.team_workspace_access.TeamWorkspaceAccessType.READ) or
                        (team_workspace_access.access_type is terrarun.models.team_workspace_access.TeamWorkspaceAccessType.CUSTOM and
                         team_workspace_access.permission_variables in [terrarun.models.team_workspace_access.TeamWorkspaceVariablesPermission.READ,
                                                                        terrarun.models.team_workspace_access.TeamWorkspaceVariablesPermission.WRITE]))

        # Check state_versions permissions
        elif state_versions is not None:
            if state_versions is terrarun.models.team_workspace_access.TeamWorkspaceStateVersionsPermissions.WRITE:
                return (self._team_has_access_type(team_workspace_access, terrarun.models.team_workspace_access.TeamWorkspaceAccessType.WRITE) or
                        (team_workspace_access.access_type is terrarun.models.team_workspace_access.TeamWorkspaceAccessType.CUSTOM and
                         team_workspace_access.permission_state_versions in [terrarun.models.team_workspace_access.TeamWorkspaceStateVersionsPermissions.WRITE]))

            elif state_versions is terrarun.models.team_workspace_access.TeamWorkspaceStateVersionsPermissions.READ:
                return (self._team_has_access_type(team_workspace_access, terrarun.models.team_workspace_access.TeamWorkspaceAccessType.READ) or
                        (team_workspace_access.access_type is terrarun.models.team_workspace_access.TeamWorkspaceAccessType.CUSTOM and
                         team_workspace_access.permission_state_versions in [terrarun.models.team_workspace_access.TeamWorkspaceStateVersionsPermissions.READ,
                                                                             terrarun.models.team_workspace_access.TeamWorkspaceStateVersionsPermissions.WRITE]))

            elif state_versions is terrarun.models.team_workspace_access.TeamWorkspaceStateVersionsPermissions.READ_OUTPUTS:
                return (self._team_has_access_type(team_workspace_access, terrarun.models.team_workspace_access.TeamWorkspaceAccessType.READ) or
                        (team_workspace_access.access_type is terrarun.models.team_workspace_access.TeamWorkspaceAccessType.CUSTOM and
                         team_workspace_access.permission_state_versions in [terrarun.models.team_workspace_access.TeamWorkspaceStateVersionsPermissions.READ_OUTPUTS,
                                                                             terrarun.models.team_workspace_access.TeamWorkspaceStateVersionsPermissions.READ,
                                                                             terrarun.models.team_workspace_access.TeamWorkspaceStateVersionsPermissions.WRITE]))

        # Check sentinel mocks permissions
        elif sentinel_mocks is not None:
            if sentinel_mocks is terrarun.models.team_workspace_access.TeamWorkspaceSentinelMocksPermission.READ:
                return (self._team_has_access_type(team_workspace_access, terrarun.models.team_workspace_access.TeamWorkspaceAccessType.READ) or
                        (team_workspace_access.access_type is terrarun.models.team_workspace_access.TeamWorkspaceAccessType.CUSTOM and
                         team_workspace_access.permission_sentinel_mocks in [terrarun.models.team_workspace_access.TeamWorkspaceSentinelMocksPermission.READ]))

        # Check workspace locking
        elif workspace_locking is not None:
            if workspace_locking is True:
                return (self._team_has_access_type(team_workspace_access, terrarun.models.team_workspace_access.TeamWorkspaceAccessType.PLAN) or
                        (team_workspace_access.access_type is terrarun.models.team_workspace_access.TeamWorkspaceAccessType.CUSTOM and
                         team_workspace_access.permission_workspace_locking))

        # Check run tasks permission
        elif run_tasks is not None:
            if run_tasks is True:
                return (self._team_has_access_type(team_workspace_access, terrarun.models.team_workspace_access.TeamWorkspaceAccessType.PLAN) or
                        (team_workspace_access.access_type is terrarun.models.team_workspace_access.TeamWorkspaceAccessType.CUSTOM and
                         team_workspace_access.permission_run_tasks))

        # Catch-all if no permissions requested
        return False


    def check_access_type(self, runs=None, variables=None,
                          state_versions=None, sentinel_mocks=None,
                          workspace_locking=None, run_tasks=None):
        """Check permission for particular access type."""
        if not self._current_user:
            return False

        # Check only one permission type is being assessed
        found_access_type = False
        for perm in [runs, variables, state_versions, sentinel_mocks, workspace_locking, run_tasks]:
            if perm is not None:
                if found_access_type:
                    raise Exception('Cannot check multiple access types in one call to check_access_type')
                found_access_type = True

        # If user is site admin, allow permission
        if self._current_user.site_admin:
            return True

        # If user is an organisation owner,
        # give all permissions
        # @TODO Owners is not yet implemented in organisation
        # if self._current_user.api_id in [owner.api_id for owner in self._workspace.organisation.owners]:
        #     return True

        user_teams = self._current_user.teams

        # Check team permissions
        for team in user_teams:
            # Iterate over all team workspace accesses for current team
            for team_workspace_access in team.workspace_accesses:
                # Check if team workspace access is for current workspace
                if team_workspace_access.workspace.id == self._workspace.id:
                    # Check workspace permissions
                    if self._check_team_access_type(
                            team_workspace_access=team_workspace_access,
                            runs=runs, variables=variables,
                            state_versions=state_versions, sentinel_mocks=sentinel_mocks,
                            workspace_locking=workspace_locking, run_tasks=run_tasks):
                        return True

        return False

    def get_api_permissions(self):
        """Return list of permissions for API"""
        return {
            permission.value: self.check_permission(permission)
            for permission in self.Permissions
        }