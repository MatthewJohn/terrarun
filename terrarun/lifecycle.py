# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import sqlalchemy
import sqlalchemy.orm

from terrarun.base_object import BaseObject
from terrarun.database import Base, Database
import terrarun.database
import terrarun.lifecycle_environment
from terrarun.environment import Environment


class Lifecycle(Base, BaseObject):

    ID_PREFIX = 'lc'
    MINIMUM_NAME_LENGTH = 3
    RESERVED_NAMES = []

    __tablename__ = 'lifecycle'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=False)
    organisation_id = sqlalchemy.Column(
        sqlalchemy.ForeignKey("organisation.id", name="fk_lifecycle_organisation_id_organisation_id"),
        nullable=False)
    organisation = sqlalchemy.orm.relationship("Organisation", back_populates="lifecycles", foreign_keys=[organisation_id])

    projects = sqlalchemy.orm.relation("Project", back_populates="lifecycle")

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
            for lifecycle_environment in self.get_lifecycle_environments()
        ]

    def get_lifecycle_environments(self):
        """Return list of lifecycle environment objects"""
        session = Database.get_session()
        return session.query(
            terrarun.lifecycle_environment.LifecycleEnvironment
        ).filter(
            terrarun.lifecycle_environment.LifecycleEnvironment.lifecycle_id==self.id
        )

    def associate_environment(self, environment, order):
        """Associate environment with lifecycle"""
        session = Database.get_session()
        lifecycle_environment = terrarun.lifecycle_environment.LifecycleEnvironment(
            lifecycle_id=self.id,
            environment_id=environment.id,
            order=order
        )
        session.add(lifecycle_environment)
        session.commit()
        return lifecycle_environment

    def get_api_details(self):
        """Return API details for lifecycle"""
        return {
            "id": self.api_id,
            "type": "lifecycles",
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
                "environments": {
                    "data": [
                        {
                            "id": lifecycle_environment.environment_id,
                            "order": lifecycle_environment.order,
                            "type": "environments"
                        }
                        for lifecycle_environment in self.get_lifecycle_environments()
                    ]
                }
            },
            "links": {
                "self": f"/api/v2/lifecycles/{self.api_id}"
            }
        }
