# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import datetime
from enum import Enum
import secrets
import string

import sqlalchemy
import sqlalchemy.orm

from terrarun.base_object import BaseObject
from terrarun.database import Base, Database
from terrarun.config import Config


class UserTokenType(Enum):
    """User token types."""

    USER_GENERATED = 'user_generated'
    UI = 'ui'


class UserToken(Base, BaseObject):

    ID_PREFIX = 'rq'
    TOKEN_CHARACTERS = string.ascii_letters + string.digits

    __tablename__ = 'user_token'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    type = sqlalchemy.Column(sqlalchemy.Enum(UserTokenType))
    created_at = sqlalchemy.Column(sqlalchemy.DateTime)
    last_used = sqlalchemy.Column(sqlalchemy.DateTime)
    expiry = sqlalchemy.Column(sqlalchemy.DateTime)
    token = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.String, default=None)

    user_id = sqlalchemy.Column(sqlalchemy.ForeignKey("user.id"), nullable=False)
    user = sqlalchemy.orm.relation("User", back_populates="user_tokens")

    @classmethod
    def generate_token(cls):
        """Generate token"""
        return '{}.terrav1.{}'.format(
            ''.join([secrets.choice(UserToken.TOKEN_CHARACTERS) for i in range(14)]),
            ''.join([secrets.choice(UserToken.TOKEN_CHARACTERS) for i in range(67)])
        )

    @classmethod
    def create(cls, user, type, description=None):
        """Create API token"""
        # Generate expiry date
        expiry = None
        if type is UserTokenType.UI:
            expiry = datetime.datetime.now() + datetime.timedelta(minutes=Config().SESSION_EXPIRY_MINS)

        # Create token object
        token = cls(
            user=user, type=type,
            expiry=expiry, token=cls.generate_token(),
            description=description
        )

        # Commit to database
        session = Database.get_session()
        session.add(token)
        session.commit()
        return token

    @classmethod
    def get_by_token(cls, token):
        """Return token by token value"""
        session = Database.get_session()
        return session.query(cls).filter(
            cls.token == token,
            sqlalchemy.or_(
                cls.expiry > datetime.datetime.now(),
                cls.expiry == None
            )
        ).first()

    def get_creation_api_details(self):
        """Create API details for created token"""
        details = self.get_api_details()
        details['attributes']['token'] = self.token
        return details

    def get_api_details(self):
        """Return API details for token"""
        return {
            "id": self.api_id,
            "type": "authentication-tokens",
            "attributes": {
                "created-at": self.created_at,
                "last-used-at": self.last_used,
                "description": self.description,
                "token": None
            },
            "relationships": {
                "created-by": {
                    "data": {
                        "id": self.user.api_id,
                        "type": "users"
                    }
                }
            }
        }
