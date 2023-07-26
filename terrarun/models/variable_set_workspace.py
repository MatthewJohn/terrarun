# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import sqlalchemy
import sqlalchemy.orm

from terrarun.database import Base


class VariableSetWorkspace(Base):
    """Define project variable sets."""

    __tablename__ = "variable_set_workspace"

    variable_set_id = sqlalchemy.Column(sqlalchemy.ForeignKey("variable_set.id", name="fk_variable_set_workspace_variable_set_id"), primary_key=True)
    variable_set = sqlalchemy.orm.relationship("VariableSet", back_populates="variable_set_workspaces", lazy='select')
    workspace_id = sqlalchemy.Column(sqlalchemy.ForeignKey("workspace.id", name="fk_variable_set_workspace_workspace_id"), primary_key=True)
    workspace = sqlalchemy.orm.relationship("Workspace", back_populates="variable_set_workspaces", lazy='select')
