# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from enum import Enum

import sqlalchemy
import sqlalchemy.orm

import terrarun.database
from terrarun.models.base_object import BaseObject
from terrarun.database import Base, Database


class VariableSet(Base, BaseObject):

    ID_PREFIX = "varset"

    __tablename__ = "variable_set"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    api_id_fk = sqlalchemy.Column(sqlalchemy.ForeignKey("api_id.id"), nullable=True)
    api_id_obj = sqlalchemy.orm.relation("ApiId", foreign_keys=[api_id_fk])

    name = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=False)
    description = sqlalchemy.Column(terrarun.database.Database.LargeString, default=None, name="description")
    is_global = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)

    organisation_id = sqlalchemy.Column(sqlalchemy.ForeignKey("organisation.id"), nullable=False)
    organisation = sqlalchemy.orm.relationship("Organisation", back_populates="variable_sets", lazy='select')

    variable_set_projects = sqlalchemy.orm.relation("VariableSetProject", back_populates="variable_set", lazy='select')
    variable_set_workspaces = sqlalchemy.orm.relation("VariableSetWorkspace", back_populates="variable_set", lazy='select')

    variables = sqlalchemy.orm.relation("Variable", back_populates="variable_set", lazy='select')
