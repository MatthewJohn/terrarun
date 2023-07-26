# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import sqlalchemy
import sqlalchemy.orm

from terrarun.database import Base


class VariableSetProject(Base):
    """Define project variable sets."""

    __tablename__ = "variable_set_project"

    variable_set_id = sqlalchemy.Column(sqlalchemy.ForeignKey("variable_set.id"), primary_key=True)
    variable_set = sqlalchemy.orm.relationship("VariableSet", back_populates="variable_set_projects", lazy='select')
    project_id = sqlalchemy.Column(sqlalchemy.ForeignKey("project.id"), primary_key=True)
    project = sqlalchemy.orm.relationship("Project", back_populates="variable_set_projects", lazy='select')
