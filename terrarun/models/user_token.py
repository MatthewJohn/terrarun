# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

import datetime
from typing import Optional
from enum import Enum
import secrets
import string

import sqlalchemy
import sqlalchemy.orm

from terrarun.models.base_object import BaseObject
import terrarun.models.user
from terrarun.database import Base, Database
from terrarun.config import Config
import terrarun.database


class UserTokenType(Enum):
    """User token types."""

    USER_GENERATED = 'user_generated'
    UI = 'ui'


class UserToken(Base, BaseObject):

    ID_PREFIX = 'rq'
    TOKEN_CHARACTERS = string.ascii_letters + string.digits

    __tablename__ = 'user_token'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    api_id_fk = sqlalchemy.Column(sqlalchemy.ForeignKey("api_id.id"), nullable=True)
    api_id_obj = sqlalchemy.orm.relationship("ApiId", foreign_keys=[api_id_fk])

    type = sqlalchemy.Column(sqlalchemy.Enum(UserTokenType))
    created_at = sqlalchemy.Column(sqlalchemy.DateTime)
    last_used = sqlalchemy.Column(sqlalchemy.DateTime)
    expiry = sqlalchemy.Column(sqlalchemy.DateTime)
    token = sqlalchemy.Column(terrarun.database.Database.GeneralString)
    description = sqlalchemy.Column(terrarun.database.Database.GeneralString, default=None)

    user_id = sqlalchemy.Column(sqlalchemy.ForeignKey("user.id"), nullable=True)
    user = sqlalchemy.orm.relationship("User", back_populates="user_tokens")

    job_id = sqlalchemy.Column(sqlalchemy.ForeignKey("run_queue.id"), nullable=True)
    job = sqlalchemy.orm.relationship("RunQueue", back_populates="user_token", uselist=False)

    @classmethod
    def generate_token(cls):
        """Generate token"""
        return '{}.terrav1.{}'.format(
            ''.join([secrets.choice(UserToken.TOKEN_CHARACTERS) for i in range(14)]),
            ''.join([secrets.choice(UserToken.TOKEN_CHARACTERS) for i in range(67)])
        )

    @classmethod
    def create_agent_job_token(cls, job):
        """Create token for agent job"""
        expiry = datetime.datetime.now() + datetime.timedelta(seconds=Config().AGENT_JOB_TIMEOUT)
        kwargs = {}
        # If the job was started by a user,
        # generate a token against the user,
        # otherwise, generate one against the job
        # @TODO Investigate enabling this - a lot of places assume that the current
        # job is available
        # if job.run.created_by:
        #     kwargs['user'] = job.run.created_by
        # else:
        kwargs['job'] = job

        token = cls(
            expiry=expiry,
            token=cls.generate_token(),
            description=f"Created for {job.run.api_id}",
            **kwargs
        )
        session = Database.get_session()
        session.add(token)
        session.commit()
        return token

    @classmethod
    def create(cls, user: 'terrarun.models.user.User', type: 'UserTokenType', description: Optional[str]=None):
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
    def get_by_token(cls, token) -> 'UserToken':
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
