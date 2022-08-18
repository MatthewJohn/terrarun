# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from enum import Enum


class OrganisationPermissions:
    """Provide interface to obtain and check permissions for user against organisation"""

    class Permissions(Enum):
        """List of allowed permissions"""
        CAN_UPDATE = "can-update"
        CAN_DESTROY = "can-destroy"
        CAN_ACCESS_VIA_TEAMS = "can-access-via-teams"
        CAN_CREATE_MODULE = "can-create-module"
        CAN_CREATE_TEAM = "can-create-team"
        CAN_CREATE_WORKSPACE = "can-create-workspace"
        CAN_MANAGE_USERS = "can-manage-users"
        CAN_MANAGE_SUBSCRIPTION = "can-manage-subscription"
        CAN_MANAGE_SSO = "can-manage-sso"
        CAN_UPDATE_OAUTH = "can-update-oauth"
        CAN_UPDATE_SENTINEL = "can-update-sentinel"
        CAN_UPDATE_SSH_KEYS = "can-update-ssh-keys"
        CAN_UPDATE_API_TOKEN = "can-update-api-token"
        CAN_TRAVERSE = "can-traverse"
        CAN_START_TRIAL = "can-start-trial"
        CAN_UPDATE_AGENT_POOLS = "can-update-agent-pools"
        CAN_MANAGE_TAGS = "can-manage-tags"
        CAN_MANAGE_VARSETS = "can-manage-varsets"
        CAN_READ_VARSETS = "can-read-varsets"
        CAN_MANAGE_PUBLIC_PROVIDERS = "can-manage-public-providers"
        CAN_CREATE_PROVIDER = "can-create-provider"
        CAN_MANAGE_PUBLIC_MODULES = "can-manage-public-modules"
        CAN_MANAGE_CUSTOM_PROVIDERS = "can-manage-custom-providers"
        CAN_MANAGE_RUN_TASKS = "can-manage-run-tasks"
        CAN_READ_RUN_TASKS = "can-read-run-tasks"

    def __init__(self, current_user, organisation):
        """Store member variables"""
        self._current_user = current_user
        self._organisation = organisation

    def check_permission(self, permission):
        """Check if user has single permission."""
        # If user is site admin, allow permission
        if self._current_user.site_admin:
            return True
        # If user is an organisation owner,
        # give all permissions
        if self._current_user.api_id in [owner.api_id for owner in self._organisation.owners]:
            return True

        user_teams = self._current_user.teams

        # Check team permissions
        #if permission in []

        return False

    def get_api_permissions(self):
        """Return list of permissions for API"""
        return {
            permission.value: self.check_permission(permission)
            for permission in self.Permissions
        }