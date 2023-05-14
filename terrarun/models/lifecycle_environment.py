# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import sqlalchemy
import sqlalchemy.orm

from terrarun.database import Base
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

    lifecycle_id = sqlalchemy.Column(sqlalchemy.ForeignKey("lifecycle.id", name="fk_lifecycle_environment_lifecycle_id_lifecycle_id"))
    lifecycle = sqlalchemy.orm.relationship("Lifecycle", back_populates="lifecycle_environments")
    environment_id = sqlalchemy.Column(sqlalchemy.ForeignKey("environment.id", name="fk_lifecycle_environment_environment_id_environment_id"))
    environment = sqlalchemy.orm.relationship("Environment", back_populates="lifecycle_environments")
    order = sqlalchemy.Column(sqlalchemy.Integer)

    __table_args__ = (
        sqlalchemy.UniqueConstraint('lifecycle_id', 'environment_id', name='_lifecycel_id_environment_id_uc'),
    )

    def get_api_details(self):
        """Return API details for lifecycle environment"""
        return {
            "id": self.api_id,
            "type": "lifecycle-environments",
            "attributes": {
                "order": self.order
            },
            "relationships": {
                "lifecycle": {
                    "data": {
                        "id": self.lifecycle.api_id,
                        "type": "lifecycles"
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
