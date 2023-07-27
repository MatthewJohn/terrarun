# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import sqlalchemy
import sqlalchemy.orm

from terrarun.database import Base
import terrarun.database


class VariableVersion(Base):

    __tablename__ = "variable_version"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    variable_id = sqlalchemy.Column(sqlalchemy.ForeignKey("variable.id", name="fk_variable_version_variable_id"), nullable=False)
    variable = sqlalchemy.orm.relationship("Variable", foreign_keys=[variable_id])

    value = sqlalchemy.Column(terrarun.database.Database.LargeString)
