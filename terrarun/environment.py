# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import sqlalchemy
import sqlalchemy.orm

from terrarun.base_object import BaseObject
from terrarun.database import Base


class Environment(Base, BaseObject):

    ID_PREFIX = 'env'
    MINIMUM_NAME_LENGTH = 3

    __tablename__ = 'environment'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)

    organisation_id = sqlalchemy.Column(
        sqlalchemy.ForeignKey("organisation.id", name="fk_environment_organisation_id_organisation_id"),
        nullable=False)
    organisation = sqlalchemy.orm.relationship("Organisation", back_populates="environments")

    workspaces = sqlalchemy.orm.relation("Workspace", back_populates="environment")
