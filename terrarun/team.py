
from enum import Enum
import sqlalchemy
import sqlalchemy.orm

from terrarun.base_object import BaseObject
from terrarun.config import Config
import terrarun.organisation
import terrarun.run
import terrarun.configuration
from terrarun.database import Base, Database


class TeamVisibility(Enum):

    ORGANIZATION = "organization"
    SECRET = "secret"


class Team(Base, BaseObject):

    ID_PREFIX = 'team'

    __tablename__ = 'team'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)

    organisation_id = sqlalchemy.Column(sqlalchemy.ForeignKey("organisation.id"), nullable=False)
    organisation = sqlalchemy.orm.relationship("Organisation", back_populates="workspaces")

    users = sqlalchemy.orm.relationship("TeamUserMembership", back_populates="team")
