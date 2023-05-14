# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from enum import Enum
import sqlalchemy
import sqlalchemy.orm

from terrarun.database import Base, Database
from terrarun.models.base_object import BaseObject
import terrarun.models.environment
import terrarun.models.lifecycle
import terrarun.models.lifecycle_environment


class LifecycleEnvironmentGroup(Base, BaseObject):
    """Define group of environment attached to a lifecycle."""

    __tablename__ = "lifecycle_environment_group"

    ID_PREFIX = 'lceg'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    api_id_fk = sqlalchemy.Column(sqlalchemy.ForeignKey("api_id.id", name="fk_lifecycle_environment_group_api_id_id"), nullable=True)
    api_id_obj = sqlalchemy.orm.relation("ApiId", foreign_keys=[api_id_fk])

    lifecycle_id = sqlalchemy.Column(sqlalchemy.ForeignKey("lifecycle.id", name="fk_lifecycle_environment_group_lifecycle_id_lifecycle_id"))
    lifecycle = sqlalchemy.orm.relationship("Lifecycle", back_populates="lifecycle_environment_groups")

    lifecycle_environments = sqlalchemy.orm.relation("LifecycleEnvironment", back_populates="lifecycle_environment_group")

    order = sqlalchemy.Column(sqlalchemy.Integer)

    # Null means all environments in previous group
    minimum_runs = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    minimum_successful_plans = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    minimum_successful_applies = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    __table_args__ = (
        sqlalchemy.UniqueConstraint('lifecycle_id', 'order', name='_lifecycle_id_order_uc'),
    )

    @classmethod
    def create(cls, lifecycle, minimum_runs=None, minimum_successful_plans=None, minimum_successful_applies=None):
        """Create environment lifecycle group"""
        # Get pre-existing group with highest group
        session = Database.get_session()
        highest_order = session.query(cls).filter(cls.lifecycle==lifecycle).order_by(cls.order.desc()).limit(1).first()

        order = 0
        if highest_order:
            order = highest_order.order + 1

        lifecycle_environment_group = cls(
            lifecycle=lifecycle,
            minimum_runs=minimum_runs,
            minimum_successful_plans=minimum_successful_plans,
            minimum_successful_applies=minimum_successful_applies,
            order=order
        )
        session.add(lifecycle_environment_group)
        session.commit()
        return lifecycle_environment_group

    def associate_environment(self, environment):
        """Associate environment with lifecycle"""
        session = Database.get_session()
        lifecycle_environment = terrarun.models.lifecycle_environment.LifecycleEnvironment(
            lifecycle_environment_group=self,
            environment=environment
        )
        session.add(lifecycle_environment)
        session.commit()
        return lifecycle_environment

    def get_api_details(self):
        """Return API details for lifecycle environment"""
        return {
            "id": self.api_id,
            "type": "lifecycle-environment-groups",
            "attributes": {
                "order": self.order,
                "minimum-runs": self.minimum_runs,
                "minimum-successful-plans": self.minimum_successful_plans,
                "minimum-successful-applies": self.minimum_successful_applies
            },
            "relationships": {
                "lifecycle": {
                    "data": {
                        "id": self.lifecycle.api_id,
                        "type": "lifecycles"
                    }
                }
            }
        }
