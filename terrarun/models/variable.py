# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from enum import Enum

import sqlalchemy
import sqlalchemy.orm

import terrarun.database
from terrarun.models.base_object import BaseObject
from terrarun.database import Base, Database


class VariableCategory(Enum):
    """Variable categories"""
    TERRAFORM = "terraform"
    ENV = "env"


class Variable(Base, BaseObject):

    ID_PREFIX = "var"

    __tablename__ = "variable"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    api_id_fk = sqlalchemy.Column(sqlalchemy.ForeignKey("api_id.id"), nullable=True)
    api_id_obj = sqlalchemy.orm.relation("ApiId", foreign_keys=[api_id_fk])

    name = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=False)
    description = sqlalchemy.Column(terrarun.database.Database.LargeString, default=None, name="description")

    workspace_id = sqlalchemy.Column(sqlalchemy.ForeignKey("workspace.id"), nullable=True)
    workspace = sqlalchemy.orm.relationship("Workspace", back_populates="variables", lazy='select')

    variable_set_id = sqlalchemy.Column(sqlalchemy.ForeignKey("workspace.id"), nullable=True)
    variable_set = sqlalchemy.orm.relationship("VariableSet", back_populates="variables", lazy='select')

    variable_version_id = sqlalchemy.Column(sqlalchemy.ForeignKey("variable_version.id"), nullable=True)
    variable_version = sqlalchemy.orm.relationship("VariableVersion")

    category = sqlalchemy.Column(sqlalchemy.Enum(VariableCategory), nullable=False)
    hcl = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)
    sensitive = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)
