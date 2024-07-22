# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

import sqlalchemy
import sqlalchemy.orm

from terrarun.models.base_object import BaseObject
from terrarun.database import Base, Database
import terrarun.database
import terrarun.models.lifecycle_environment


class Environment(Base, BaseObject):

    ID_PREFIX = 'env'
    MINIMUM_NAME_LENGTH = 3
    RESERVED_NAMES = []

    __tablename__ = 'environment'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    api_id_fk = sqlalchemy.Column(sqlalchemy.ForeignKey("api_id.id"), nullable=True)
    api_id_obj = sqlalchemy.orm.relation("ApiId", foreign_keys=[api_id_fk])

    name = sqlalchemy.Column(terrarun.database.Database.GeneralString)
    description = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=True)

    organisation_id = sqlalchemy.Column(
        sqlalchemy.ForeignKey("organisation.id", name="fk_environment_organisation_id_organisation_id"),
        nullable=False)
    organisation = sqlalchemy.orm.relationship("Organisation", back_populates="environments")

    workspaces = sqlalchemy.orm.relation("Workspace", back_populates="environment")
    lifecycle_environments = sqlalchemy.orm.relation("LifecycleEnvironment", back_populates="environment")

    @classmethod
    def get_by_name_and_organisation(cls, name, organisation):
        """Obtain environment by organisation and name"""
        session = Database.get_session()
        return session.query(cls).filter(cls.name==name, cls.organisation==organisation).first()

    @classmethod
    def validate_new_name(cls, organisation, name):
        """Ensure environment does not already exist and name isn't reserved"""
        session = Database.get_session()
        existing_name = session.query(cls).filter(
            cls.organisation == organisation,
            cls.name == name
        ).first()
        if existing_name:
            return False
        if name in cls.RESERVED_NAMES:
            return False
        if len(name) < cls.MINIMUM_NAME_LENGTH:
            return False
        return True

    @classmethod
    def create(cls, organisation, name, description=None):
        """Create lifecycle"""
        if not cls.validate_new_name(organisation, name):
            return None

        lifecycle = cls(
            organisation=organisation,
            name=name,
            description=description
        )
        session = Database.get_session()
        session.add(lifecycle)
        session.commit()

        return lifecycle

    def get_api_details(self):
        """Return API details for environment"""
        return {
            "id": self.api_id,
            "type": "environments",
            "attributes": {
                "name": self.name,
                "description": self.description
            },
            "relationships": {
                "organization": {
                    "data": {
                        "id": self.organisation.name,
                        "type": "organizations"
                    }
                },
                "lifecycle-environments": {
                    "data": [
                        {
                            "id": lifecycle_environment.api_id,
                            "type": "lifecycle-environments"
                        }
                        for lifecycle_environment in self.lifecycle_environments
                    ]
                }
            },
            "links": {
                "self": f"/api/v2/environments/{self.api_id}"
            }
        }
