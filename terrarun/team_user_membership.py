
import sqlalchemy
import sqlalchemy.orm

from terrarun.database import Base


TEAM_USER_MEMBERSHIP_TABLE = sqlalchemy.Table(
    "team_user_membership",
    Base.metadata,
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("user.id"), primary_key=True),
    sqlalchemy.Column("team_id", sqlalchemy.ForeignKey("team.id"), primary_key=True),
)
