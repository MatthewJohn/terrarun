# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import sqlalchemy
import sqlalchemy.orm

from terrarun.base_object import BaseObject
from terrarun.database import Base


class MetaWorkspace(Base, BaseObject):

    ID_PREFIX = 'mws'
    MINIMUM_NAME_LENGTH = 3

    __tablename__ = 'meta_workspace'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)

    organisation_id = sqlalchemy.Column(sqlalchemy.ForeignKey(
        "organisation.id", name="fk_meta_workspace_organisation_id_organisation_id"),
        nullable=False)
    organisation = sqlalchemy.orm.relationship("Organisation", back_populates="meta_workspaces")

    workspaces = sqlalchemy.orm.relation("Workspace", back_populates="meta_workspace")

    lifecycle_id = sqlalchemy.Column(
        sqlalchemy.ForeignKey("lifecycle.id", name="fk_meta_workspace_lifecycle_id_lifecycle_id"),
        nullable=False)
    lifecycle = sqlalchemy.orm.relationship("Lifecycle", back_populates="meta_workspaces")
