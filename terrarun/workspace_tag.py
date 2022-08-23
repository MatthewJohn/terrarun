# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import sqlalchemy
import sqlalchemy.orm

from terrarun.database import Base


class WorkspaceTag(Base):
    """Define workspace tags."""

    __tablename__ = "workspace_tag"

    workspace_id = sqlalchemy.Column(sqlalchemy.ForeignKey("workspace.id"), primary_key=True)
    workspace = sqlalchemy.orm.relationship("Workspace", back_populates="tags")
    tag_id = sqlalchemy.Column(sqlalchemy.ForeignKey("tag.id"), primary_key=True)
    tag = sqlalchemy.orm.relationship("Tag", back_populates="workspaces")
