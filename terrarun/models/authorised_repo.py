

from enum import Enum
import sqlalchemy
import sqlalchemy.orm

import terrarun.database
from terrarun.database import Base, Database
from terrarun.models.base_object import BaseObject
import terrarun.utils


class AuthorisedRepo(Base, BaseObject):

    ID_PREFIX = ''
    RESERVED_NAMES = []

    __tablename__ = 'authorised_repo'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=sqlalchemy.sql.func.now())

    last_checked_changes = sqlalchemy.Column(sqlalchemy.DateTime, default=None)

    provider_id = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=True)
    external_id = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=True)
    display_identifier = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=True)
    name = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=True)

    oauth_token_id = sqlalchemy.Column(sqlalchemy.ForeignKey(
        "oauth_token.id", name="fk_authorised_repo_oauth_token_id_oauth_token_id"),
        nullable=False
    )
    oauth_token = sqlalchemy.orm.relationship("OauthToken", back_populates="authorised_repos")

    @classmethod
    def get_by_provider_id(cls, oauth_token, provider_id):
        """Get authorised app by external Id and oauth client"""
        session = Database.get_session()
        return session.query(cls).filter(cls.oauth_token==oauth_token, cls.provider_id==provider_id).first()

    def get_api_details(self):
        """Return API details"""
        return {
            "id": self.external_id,
            "type": "authorized-repos",
            "attributes": {
                "display-identifier": self.display_identifier,
                "name": self.name
            },
            "relationships": {
                "oauth-token": {
                    "data": {
                        "id": self.oauth_token.api_id,
                        "type": "oauth-tokens"
                    }
                }
            }
        }