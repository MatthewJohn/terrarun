# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import sqlalchemy
import sqlalchemy.orm

from terrarun.base_object import BaseObject
from terrarun.database import Base, Database
import terrarun.lifecycle_environment


class Environment(Base, BaseObject):

    ID_PREFIX = 'env'
    MINIMUM_NAME_LENGTH = 3
    RESERVED_NAMES = []

    __tablename__ = 'environment'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)

    organisation_id = sqlalchemy.Column(
        sqlalchemy.ForeignKey("organisation.id", name="fk_environment_organisation_id_organisation_id"),
        nullable=False)
    organisation = sqlalchemy.orm.relationship("Organisation", back_populates="environments")

    workspaces = sqlalchemy.orm.relation("Workspace", back_populates="environment")

    @classmethod
    def validate_new_name_id(cls, organisation, name):
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
        return True

    @classmethod
    def create(cls, organisation, name):
        """Create lifecycle"""
        if not cls.validate_new_name_id(organisation, name):
            return None

        lifecycle = cls(organisation=organisation, name=name)
        session = Database.get_session()
        session.add(lifecycle)
        session.commit()

        return lifecycle

    def get_lifecycle_environments(self):
        """Return list of lifecycle environment objects"""
        session = Database.get_session()
        return session.query(
            terrarun.lifecycle_environment.LifecycleEnvironment
        ).filter(
            terrarun.lifecycle_environment.LifecycleEnvironment.environment_id==self.id
        )

    def get_api_details(self):
        """Return API details for environment"""
        return {
            "id": self.api_id,
            "type": "environments",
            "attributes": {
                "name": self.name
            },
            "relationships": {
                "organization": {
                    "data": {
                        "id": self.organisation.name,
                        "type": "organizations"
                    }
                },
                "lifecycles": {
                    "data": [
                        {
                            "id": lifecycle_environment.lifecycle_id,
                            "type": "lifecycles"
                        }
                        for lifecycle_environment in self.get_lifecycle_environments()
                    ]
                }
            },
            "links": {
                "self": f"/api/v2/environments/{self.api_id}"
            }
        }
