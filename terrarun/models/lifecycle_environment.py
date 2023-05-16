# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import sqlalchemy
import sqlalchemy.orm

from terrarun.database import Base, Database
from terrarun.errors import OrganisationMixError
from terrarun.models.base_object import BaseObject
import terrarun.models.environment
import terrarun.models.lifecycle


class LifecycleEnvironment(Base, BaseObject):
    """Define lifecycle environment."""

    __tablename__ = "lifecycle_environment"

    ID_PREFIX = 'lce'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    api_id_fk = sqlalchemy.Column(sqlalchemy.ForeignKey("api_id.id", name="fk_lifecycle_environment_api_id_id"), nullable=True)
    api_id_obj = sqlalchemy.orm.relation("ApiId", foreign_keys=[api_id_fk])

    lifecycle_environment_group_id = sqlalchemy.Column(sqlalchemy.ForeignKey(
        "lifecycle_environment_group.id",
        name="fk_lifecycle_environment_lifecycle_environment_group_id"),
        nullable=False)
    lifecycle_environment_group = sqlalchemy.orm.relationship("LifecycleEnvironmentGroup", back_populates="lifecycle_environments")
    environment_id = sqlalchemy.Column(sqlalchemy.ForeignKey(
        "environment.id", name="fk_lifecycle_environment_environment_id_environment_id"), nullable=False)
    environment = sqlalchemy.orm.relationship("Environment", back_populates="lifecycle_environments")

    __table_args__ = (
        sqlalchemy.UniqueConstraint('lifecycle_environment_group_id', 'environment_id', name='_lifecycle_environment_group_id_environment_id_uc'),
    )

    @classmethod
    def create(cls, lifecycle_environment_group, environment):
        """Create lifecycle environment"""
        if lifecycle_environment_group.lifecycle.organisation != environment.organisation:
            raise OrganisationMixError("Cannot assign an environment and lifecycle environment group from different organisations")#

        lifecycle_environment = cls(lifecycle_environment_group=lifecycle_environment_group, environment=environment)
        session = Database.get_session()
        session.add(lifecycle_environment)
        session.commit()
        return lifecycle_environment

    def delete(self):
        """Delete lifecycle environment"""
        session = Database.get_session()
        session.delete(self)
        session.commit()

    def get_api_details(self):
        """Return API details for lifecycle environment"""
        return {
            "id": self.api_id,
            "type": "lifecycle-environments",
            "attributes": {
                "environment-name": self.environment.name
            },
            "relationships": {
                "lifecycle": {
                    "data": {
                        "id": self.lifecycle_environment_group.lifecycle.api_id,
                        "type": "lifecycles"
                    }
                },
                "lifecycle-environment-group": {
                    "data": {
                        "id": self.lifecycle_environment_group.api_id,
                        "type": "lifecycle-environment-groups"
                    }
                },
                "environment": {
                    "data": {
                        "id": self.environment.api_id,
                        "type": "environments"
                    }
                }
            }
        }
