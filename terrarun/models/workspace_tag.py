# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

import sqlalchemy
import sqlalchemy.orm

from terrarun.database import Base


class WorkspaceTag(Base):
    """Define workspace tags."""

    __tablename__ = "workspace_tag"

    workspace_id = sqlalchemy.Column(sqlalchemy.ForeignKey("workspace.id"), primary_key=True)
    tag_id = sqlalchemy.Column(sqlalchemy.ForeignKey("tag.id"), primary_key=True)
