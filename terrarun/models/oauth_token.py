

from enum import Enum
import sqlalchemy
import sqlalchemy.orm

import terrarun.database
from terrarun.database import Base, Database
from terrarun.models.base_object import BaseObject
import terrarun.utils


class OauthToken(Base, BaseObject):

    ID_PREFIX = 'ot'
    RESERVED_NAMES = []

    __tablename__ = 'oauth_token'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=sqlalchemy.sql.func.now())

    service_provider_user = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=True)

    oauth_client_id = sqlalchemy.Column(sqlalchemy.ForeignKey(
        "oauth_client.id", name="fk_oauth_token_oauth_cient_id_oauth_client_id"),
        nullable=False
    )
    oauth_client = sqlalchemy.orm.relationship("OauthClient", back_populates="oauth_tokens")
    ssh_key = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=True)
    token = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=True)

    @classmethod
    def create(cls, oauth_client, service_provider_user, token, session=None):
        """Create Oauth Token"""
        should_commit = False
        if not session:
            session = Database.get_session()
            should_commit = True

        oauth_token = cls(
            token=token,
            oauth_client=oauth_client,
            service_provider_user=service_provider_user
        )

        session = Database.get_session()
        session.add(oauth_token)
        if should_commit:
            session.commit()
        return oauth_token

    @classmethod
    def get_by_oauth_client_and_user(cls, oauth_client, user):
        """Return oauth tokens by oauth client and user"""
        session = Database.get_session()
        session.query(cls).filter(cls.oauth_client==oauth_client, cls.user==user).first()

    def delete(self):
        """Delete object"""
        session = Database.get_session()
        session.delete(self)
        session.commit()

    def get_relationship(self):
        """Return relationship data for oauth token."""
        return {
            "id": self.api_id,
            "type": "oauth-tokens"
        }

    def get_api_details(self):
        """Return API details"""
        return {
            "id": self.api_id,
            "type": "oauth-tokens",
            "attributes": {
                "created-at": terrarun.utils.datetime_to_json(self.created_at),
                "service-provider-user": self.service_provider_user,
                "has-ssh-key": bool(self.ssh_key)
            },
            "relationships": {
                "oauth-client": {
                    "data": {
                        "id": self.oauth_client.api_id,
                        "type": "oauth-clients"
                    },
                    "links": {
                        "related": f"/api/v2/oauth-clients/{self.oauth_client.api_id}"
                    }
                }
            },
            "links": {
                "self": f"/api/v2/oauth-tokens/{self.api_id}"
            }
        }
