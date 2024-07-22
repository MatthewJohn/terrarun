# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

from enum import Enum


class UserPermissions:
    """Manage user permission logic"""

    class Permissions(Enum):
        """User permissions"""

        CAN_CREATE_ORGANISATIONS = "can-create-organizations"
        CAN_CHANGE_EMAIL = "can-change-email"
        CAN_CHANGE_USERNAME = "can-change-username"
        CAN_MANAGE_USER_TOKENS = "can-manage-user-tokens"

    def __init__(self, current_user, user):
        """Store member variables"""
        self._current_user = current_user
        self._user = user

    def check_permission(self, permission):
        """Check if user has single permission."""
        # If user is site admin, allow permission
        if self._user.site_admin:
            return True

        # Only site admins can create organisations
        if permission is self.Permissions.CAN_CREATE_ORGANISATIONS:
            return False
        
        elif permission in [self.Permissions.CAN_CHANGE_EMAIL,
                            self.Permissions.CAN_CHANGE_USERNAME,
                            self.Permissions.CAN_MANAGE_USER_TOKENS]:
            # If the target user is the same as the acting user
            if self._current_user.id == self._user.id:
                # Service accounts cannot manage their own
                if self._user.service_account:
                    return False
                else:
                    # @TODO Should SSO determine whether a user can change their
                    # username/email
                    return True

        return False

    def get_api_permissions(self):
        """Return list of permissions for API"""
        return {
            permission.value: self.check_permission(permission)
            for permission in self.Permissions
        }
