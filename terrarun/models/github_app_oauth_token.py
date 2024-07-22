# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0


import sqlalchemy
import sqlalchemy.orm

from terrarun.database import Base, Database
from terrarun.models.base_object import BaseObject
import terrarun.database
from terrarun.utils import datetime_to_json


class GithubAppOauthToken(Base, BaseObject):

    ID_PREFIX = 'ghaot'
    RESERVED_NAMES = []

    __tablename__ = 'github_app_oauth_token'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    api_id_fk = sqlalchemy.Column(sqlalchemy.ForeignKey("api_id.id"), nullable=True)
    api_id_obj = sqlalchemy.orm.relation("ApiId", foreign_keys=[api_id_fk])

    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=sqlalchemy.sql.func.now())

    oauth_client_id = sqlalchemy.Column(sqlalchemy.ForeignKey(
        "oauth_client.id", name="fk_github_app_oauth_token_oauth_client_oauth_client_id"),
        nullable=False
    )
    oauth_client = sqlalchemy.orm.relationship("OauthClient")
    github_username = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=False)
    token = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=False)

    user_id = sqlalchemy.Column(sqlalchemy.ForeignKey(
        "user.id", name="fk_github_app_oauth_token_user_id_user_id"),
        nullable=False
    )
    user = sqlalchemy.orm.relationship("User")

    @classmethod
    def create(cls, oauth_client, user, token, github_username):
        """Create github app oauth token"""
        session = terrarun.database.Database.get_session()

        # Delete any pre-existing tokens for oauth client and user
        session.query(cls).filter(
            cls.oauth_client==oauth_client,
            cls.user==user
        ).delete()

        github_app_oauth_token = cls(
            oauth_client=oauth_client,
            user=user,
            token=token,
            github_username=github_username
        )
        session.add(github_app_oauth_token)
        session.commit()
        return github_app_oauth_token

    @classmethod
    def get_by_user(cls, user):
        """Get github oauth tokens by user"""
        session = Database.get_session()
        return session.query(cls).filter(cls.user==user).all()

    def get_api_details(self):
        """Return API details for github app oauth token"""
        return {
            "id": self.api_id,
            "type": "github-app-oauth-tokens",
            "attributes": {
                "github-username": self.github_username,
                "created-at": datetime_to_json(self.created_at)
            },
            "relationships": {
                "user": {
                    "data": self.user.get_relationship(),
                    "link": f"/api/v2/users/{self.user.api_id}"
                },
                "oauth-client": {
                    "data": self.oauth_client.get_relationship(),
                    "link": f"/api/v2/oauth-clients/{self.oauth_client.api_id}"
                }
            }
        }
