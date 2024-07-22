# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

import sqlalchemy
import sqlalchemy.orm

from terrarun.database import Base


class OrganisationOwner(Base):
    """Define organisation owner."""

    __tablename__ = "organisation_owner"

    organisation_id = sqlalchemy.Column(sqlalchemy.ForeignKey("organisation.id"), primary_key=True)
    user_id = sqlalchemy.Column(sqlalchemy.ForeignKey("user.id"), primary_key=True)
    organisation = sqlalchemy.orm.relationship("Organisation")
    user = sqlalchemy.orm.relationship("User")
