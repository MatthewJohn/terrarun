# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

import sqlalchemy
import sqlalchemy.orm

from terrarun.database import Base


class TeamUserMembership(Base):
    """Define team user memberships."""

    __tablename__ = "team_user_membership"

    ID_PREFIX = "ou"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    api_id_fk = sqlalchemy.Column(sqlalchemy.ForeignKey("api_id.id", name="team_user_membership_api_id"), nullable=True)
    api_id_obj = sqlalchemy.orm.relation("ApiId", foreign_keys=[api_id_fk])

    team_id = sqlalchemy.Column(sqlalchemy.ForeignKey("team.id"), nullable=False)
    team = sqlalchemy.orm.relationship("Team", back_populates="users")
    user_id = sqlalchemy.Column(sqlalchemy.ForeignKey("user.id"), nullable=False)
    user = sqlalchemy.orm.relationship("User", back_populates="teams")

    __table_args__ = (
        sqlalchemy.UniqueConstraint('team_id', 'user_id', name='_team_id_user_id_uc'),
    )
