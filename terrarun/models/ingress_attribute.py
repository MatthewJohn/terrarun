# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0


from re import L
import sqlalchemy
import sqlalchemy.orm

from terrarun.database import Base, Database
from terrarun.models.base_object import BaseObject
import terrarun.database
from terrarun.models.blob import Blob
import terrarun.utils


class IngressAttribute(Base, BaseObject):

    ID_PREFIX = 'ia'
    RESERVED_NAMES = []

    __tablename__ = 'ingress_attribute'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    api_id_fk = sqlalchemy.Column(sqlalchemy.ForeignKey("api_id.id"), nullable=True)
    api_id_obj = sqlalchemy.orm.relationship("ApiId", foreign_keys=[api_id_fk])

    branch = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=False)
    commit_message_blob_id = sqlalchemy.Column(sqlalchemy.ForeignKey("blob.id", name="ingress_attribute_commit_message_blob_id_blob_id"), nullable=True)
    commit_message_blob = sqlalchemy.orm.relationship("Blob", foreign_keys=[commit_message_blob_id])
    commit_sha = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=False)
    parent_commit_sha = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=True)
    on_default_branch = sqlalchemy.Column(sqlalchemy.Boolean)
    pull_request_id = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=True)
    pull_request_title = sqlalchemy.Column(terrarun.database.Database.LargeString, nullable=True)
    pull_request_body = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=True)
    tag = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=True)
    sender_username = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=True)
    sender_avatar_url = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=True)

    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=sqlalchemy.sql.func.now())

    authorised_repo_id = sqlalchemy.Column(sqlalchemy.ForeignKey(
        "authorised_repo.id", name="fk_ingress_attributes_authorised_repo_authorised_repo"),
        nullable=False
    )
    authorised_repo = sqlalchemy.orm.relationship("AuthorisedRepo", back_populates="ingress_attributes")

    creator_user_id = sqlalchemy.Column(sqlalchemy.ForeignKey(
        "user.id", name="fk_ingress_attributes_creator_user_id_user_id"),
        nullable=True
    )
    creator = sqlalchemy.orm.relationship("User", back_populates="ingress_attributes")

    configuration_versions = sqlalchemy.orm.relationship("ConfigurationVersion", back_populates="ingress_attribute")

    @classmethod
    def create(cls, authorised_repo, commit_sha, branch, pull_request_id, creator, tag):
        """Create new ingress attributes"""
        service_provider_instance = authorised_repo.oauth_token.oauth_client.service_provider_instance
        commit_details = service_provider_instance.get_commit_ingress_data(
            authorised_repo, commit_sha)
        commit_message = commit_details.get("commit_message")
        if "commit_message" in commit_details:
            del commit_details["commit_message"]

        pull_request_title = None
        pull_request_body = None
        # Not currently supported
        # if pull_request_id:
        #     pull_request_title, pull_request_body = service_provider_instance.get_pull_request_details(
        #         authorised_repo, pull_request_id)

        ingress_attribute = cls(
            authorised_repo=authorised_repo,
            commit_sha=commit_sha,
            branch=branch,
            tag=tag,
            creator=creator,
            # Obtain additional attributes from authorised repo
            pull_request_id=pull_request_id,
            pull_request_title=pull_request_title,
            pull_request_body=pull_request_body,
            **commit_details
        )

        session = Database.get_session()
        session.add(ingress_attribute)
        session.commit()
        ingress_attribute.commit_message = commit_message
        return ingress_attribute

    @property
    def commit_message(self):
        """Return commit message blob"""
        if self.commit_message_blob and self.commit_message_blob.data:
            return self.commit_message_blob.data.decode('utf-8')
        return None

    @commit_message.setter
    def commit_message(self, value):
        """Set commit message"""
        session = Database.get_session()

        if self.commit_message_blob:
            commit_message_blob = self.commit_message_blob
            session.refresh(commit_message_blob)
        else:
            commit_message_blob = Blob()

        commit_message_blob.data = bytes(value, 'utf-8')

        session.add(commit_message_blob)
        session.refresh(self)
        self.commit_message_blob = commit_message_blob
        session.add(self)
        session.commit()

    @classmethod
    def get_by_authorised_repo_and_commit_sha(cls, authorised_repo, commit_sha):
        """Get instance by authorised repo and commit sha"""
        session = Database.get_session()
        return session.query(cls).filter(cls.authorised_repo==authorised_repo, cls.commit_sha==commit_sha).first()

    @property
    def clone_url(self):
        """Return clone URL for repo"""
        return self.authorised_repo.oauth_token.oauth_client.service_provider_instance.clone_url

    @property
    def commit_url(self):
        """Return commit URL"""
        return self.authorised_repo.oauth_token.oauth_client.service_provider_instance.get_commit_url(
            authorised_repo=self.authorised_repo, commit_sha=self.commit_sha)

    @property
    def compare_url(self):
        """Return compare URL"""
        return self.authorised_repo.oauth_token.oauth_client.service_provider_instance.get_commit_compare_url(
            authorised_repo=self.authorised_repo, commit_sha=self.commit_sha, parent_commit_sha=self.parent_commit_sha)

    @property
    def pull_request_url(self):
        """Get pull request URL"""
        if self.pull_request_id:
            return self.authorised_repo.oauth_token.oauth_client.service_provider_instance.get_pull_request_url_from_id(
                self.pull_request_id)
        return None

    @property
    def sender_html_url(self):
        """Return HTML URL for sender"""
        return self.authorised_repo.oauth_token.oauth_client.service_provider_instance.sender_html_url_from_username(
            self.authorised_repo,
            self.sender_username
        )

    def get_api_details(self):
        """Return API details"""
        return {
            "id": self.api_id,
            "type": "ingress-attributes",
            "attributes": {
                "branch": self.branch,
                "clone-url": self.authorised_repo.clone_url,
                "commit-message": self.commit_message,
                "commit-sha": self.commit_sha,
                "commit-url": self.commit_url,
                "compare-url": self.compare_url,
                "identifier": self.authorised_repo.name,
                "is-pull-request": bool(self.pull_request_id),
                "on-default-branch": self.on_default_branch,
                "pull-request-number": self.pull_request_id,
                "pull-request-url": self.pull_request_url,
                "pull-request-title": self.pull_request_title,
                "pull-request-body": self.pull_request_body,
                "tag": self.tag,
                "sender-username": self.sender_username,
                "sender-avatar-url": self.sender_avatar_url,
                "sender-html-url": self.sender_html_url,

                # Custom attribute(s)
                "created-at": terrarun.utils.datetime_to_json(self.created_at)
            },
            "relationships": {
                "created-by": {
                    "data": {
                        "id": self.creator.api_id,
                        "type": "users"
                    },
                    "links": {
                        "related": f"/api/v2/ingress-attributes/{self.api_id}/created-by"
                    }
                } if self.creator else {}
            },
            "links": {
                "self": f"/api/v2/ingress-attributes/{self.api_id}"
            }
        }