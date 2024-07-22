# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

import re
import sqlalchemy
import sqlalchemy.orm

from terrarun.models.base_object import BaseObject
from terrarun.database import Base, Database
import terrarun.database
import terrarun.models.lifecycle_environment
from terrarun.models.environment import Environment


class Lifecycle(Base, BaseObject):

    ID_PREFIX = 'lc'
    MINIMUM_NAME_LENGTH = 3
    RESERVED_NAMES = []

    __tablename__ = 'lifecycle'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    api_id_fk = sqlalchemy.Column(sqlalchemy.ForeignKey("api_id.id"), nullable=True)
    api_id_obj = sqlalchemy.orm.relation("ApiId", foreign_keys=[api_id_fk])

    name = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=False)
    description = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=True)

    # Whether to allow per-workspace VCS configurations
    allow_per_workspace_vcs = sqlalchemy.Column(sqlalchemy.Boolean, default=False, nullable=False)

    organisation_id = sqlalchemy.Column(
        sqlalchemy.ForeignKey("organisation.id", name="fk_lifecycle_organisation_id_organisation_id"),
        nullable=False)
    organisation = sqlalchemy.orm.relationship("Organisation", back_populates="lifecycles", foreign_keys=[organisation_id])

    projects = sqlalchemy.orm.relation("Project", back_populates="lifecycle")
    lifecycle_environment_groups = sqlalchemy.orm.relation("LifecycleEnvironmentGroup", back_populates="lifecycle")

    @classmethod
    def get_by_name_and_organisation(cls, name, organisation):
        """Obtain environment by organisation and name"""
        session = Database.get_session()
        return session.query(cls).filter(cls.name==name, cls.organisation==organisation).first()

    @classmethod
    def validate_new_name(cls, organisation, name):
        """Ensure lifecycle does not already exist and name isn't reserved"""
        session = Database.get_session()
        existing_org = session.query(cls).filter(
            cls.organisation == organisation,
            cls.name == name
        ).first()
        if existing_org:
            return False
        if name in cls.RESERVED_NAMES:
            return False
        if len(name) < cls.MINIMUM_NAME_LENGTH:
            return False
        if not re.match(r"^[a-zA-z0-9-_]+$", name):
            return False
        return True

    @classmethod
    def create(cls, organisation, name):
        """Create lifecycle"""
        if not cls.validate_new_name(organisation, name):
            return None

        lifecycle = cls(organisation=organisation, name=name)
        session = Database.get_session()
        session.add(lifecycle)
        session.commit()

        return lifecycle

    @property
    def environments(self):
        """Return list of environments"""
        return [
            Environment.get_by_id(lifecycle_environment.environment_id)
            for lifecycle_environment in self.lifecycle
        ]

    def get_api_details(self):
        """Return API details for lifecycle"""
        return {
            "id": self.api_id,
            "type": "lifecycles",
            "attributes": {
                "name": self.name,
                "description": self.description,
                "allow-per-workspace-vcs": self.allow_per_workspace_vcs
            },
            "relationships": {
                "organization": {
                    "data": {
                        "id": self.organisation.name,
                        "type": "organizations"
                    }
                },
                "environments": {
                    "data": [
                        {
                            "id": lifecycle_environment.environment.api_id,
                            "type": "environments"
                        }
                        for lifecycle_environment_group in self.lifecycle_environment_groups
                        for lifecycle_environment in lifecycle_environment_group.lifecycle_environments
                    ]
                },
                "environment-lifecycles": {
                    "data": [
                        {
                            "id": lifecycle_environment.api_id,
                            "type": "lifecycle-environments"
                        }
                        for lifecycle_environment_group in self.lifecycle_environment_groups
                        for lifecycle_environment in lifecycle_environment_group.lifecycle_environments
                    ]
                },
                "environment-lifecycle-groups": {
                    "data": [
                        {
                            "id": lifecycle_environment_group.api_id,
                            "type": "lifecycle-environments"
                        }
                        for lifecycle_environment_group in self.lifecycle_environment_groups
                    ]
                }
            },
            "links": {
                "self": f"/api/v2/lifecycles/{self.api_id}"
            }
        }
