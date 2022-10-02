# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import sqlalchemy
import sqlalchemy.orm

from terrarun.database import Base


class LifecycleEnvironment(Base):
    """Define lifecycle environment."""

    __tablename__ = "lifecycle_environment"

    lifecycle_id = sqlalchemy.Column(sqlalchemy.ForeignKey("lifecycle.id"), primary_key=True)
    environment_id = sqlalchemy.Column(sqlalchemy.ForeignKey("environment.id"), primary_key=True)
    order = sqlalchemy.Column(sqlalchemy.Integer)
