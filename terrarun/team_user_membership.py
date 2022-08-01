
import sqlalchemy
import sqlalchemy.orm

from terrarun.database import Base


class TeamUserMembership(Base):
    """Define team user memberships."""

    __tablename__ = "team_user_membership"

    team_id = sqlalchemy.Column(sqlalchemy.ForeignKey("team.id"), primary_key=True)
    user_id = sqlalchemy.Column(sqlalchemy.ForeignKey("user.id"), primary_key=True)
    team = sqlalchemy.orm.relationship("Team", back_populates="users")
    user = sqlalchemy.orm.relationship("User", back_populates="teams")
