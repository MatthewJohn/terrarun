# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import sqlalchemy
import sqlalchemy.orm

from terrarun.base_object import BaseObject
from terrarun.database import Base


class Lifecycle(Base, BaseObject):

    ID_PREFIX = 'lc'
    MINIMUM_NAME_LENGTH = 3

    __tablename__ = 'lifecycle'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    organisation_id = sqlalchemy.Column(
        sqlalchemy.ForeignKey("organisation.id", name="fk_lifecycle_organisation_id_organisation_id"),
        nullable=False)
    organisation = sqlalchemy.orm.relationship("Organisation", back_populates="lifecycles", foreign_keys=[organisation_id])

    meta_workspaces = sqlalchemy.orm.relation("MetaWorkspace", back_populates="lifecycle")