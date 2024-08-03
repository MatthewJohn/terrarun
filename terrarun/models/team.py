# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

from enum import Enum
import sqlalchemy
import sqlalchemy.orm

from terrarun.models.base_object import BaseObject
from terrarun.config import Config
import terrarun.database
import terrarun.models.organisation
import terrarun.models.run
import terrarun.models.configuration
from terrarun.database import Base, Database


class TeamVisibility(Enum):

    ORGANIZATION = "organization"
    SECRET = "secret"


class Team(Base, BaseObject):

    ID_PREFIX = 'team'

    __tablename__ = 'team'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    api_id_fk = sqlalchemy.Column(sqlalchemy.ForeignKey("api_id.id"), nullable=True)
    api_id_obj = sqlalchemy.orm.relationship("ApiId", foreign_keys=[api_id_fk])

    name = sqlalchemy.Column(terrarun.database.Database.GeneralString)

    organisation_id = sqlalchemy.Column(sqlalchemy.ForeignKey("organisation.id"), nullable=False)
    organisation = sqlalchemy.orm.relationship("Organisation", back_populates="teams")

    sso_team_id = sqlalchemy.Column(terrarun.database.Database.GeneralString, default=None)
    visibility = sqlalchemy.Column(sqlalchemy.Enum(TeamVisibility))

    # Team organisation permissions
    manage_policies = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    manage_policy_overrides = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    manage_run_tasks = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    manage_vcs_settings = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    manage_workspaces = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    manage_providers = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    manage_modules = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    users = sqlalchemy.orm.relationship("TeamUserMembership", back_populates="team")

    workspace_accesses = sqlalchemy.orm.relationship("TeamWorkspaceAccess", back_populates="team")

    def get_api_details(self):
        """Return API details for organisation"""
        return {
            "attributes": {
                "name": self.name,
                "sso-team-id": self.sso_team_id,
                "organization-access": {
                    "manage-policies": self.manage_policies,
                    "manage-policy-overrides": self.manage_policy_overrides,
                    "manage-run-tasks": self.manage_run_tasks,
                    "manage-vcs-settings": self.manage_vcs_settings,
                    "manage-workspaces": self.manage_workspaces,
                    "manage-providers": self.manage_providers,
                    "manage-modules": self.manage_modules
                },
                "permissions": {
                    "can-update-membership": True,
                    "can-destroy": True,
                    "can-update-organization-access": True,
                    "can-update-api-token": True,
                    "can-update-visibility": True
                },
                "users-count": len(self.users),
                "visibility": self.visibility.value
            },
            "id": self.api_id,
            "links": {
                "self": f"/api/v2/teams/{self.api_id}"
            },
            "relationships": {
                "authentication-token": {
                    "meta": {}
                },
                "users": {
                    "data": [
                        { "id": user.username, "type": "users" }
                        for user in self.users
                    ]
                }
            },
            "type": "teams"
        }
