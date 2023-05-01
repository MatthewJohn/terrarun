# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import sqlalchemy
import sqlalchemy.orm

from terrarun.database import Base
import terrarun.models.environment
import terrarun.models.lifecycle


class LifecycleEnvironment(Base):
    """Define lifecycle environment."""

    __tablename__ = "lifecycle_environment"

    lifecycle_id = sqlalchemy.Column(sqlalchemy.ForeignKey("lifecycle.id"), primary_key=True)
    environment_id = sqlalchemy.Column(sqlalchemy.ForeignKey("environment.id"), primary_key=True)
    order = sqlalchemy.Column(sqlalchemy.Integer)

    @property
    def environment(self):
        """Return environment"""
        return terrarun.models.environment.Environment.get_by_id(self.environment_id)

    @property
    def lifecycle(self):
        """Return lifecycle"""
        return terrarun.models.lifecycle.Lifecycle.get_by_id(self.lifecycle_id)
