
from re import L
import sqlalchemy
import sqlalchemy.orm

from terrarun.database import Base, Database
from terrarun.models.base_object import BaseObject
import terrarun.database
from terrarun.utils import datetime_to_json


class IngressAttribute(Base, BaseObject):

    ID_PREFIX = 'ia'
    RESERVED_NAMES = []

    __tablename__ = 'ingress_attribute'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    api_id_fk = sqlalchemy.Column(sqlalchemy.ForeignKey("api_id.id"), nullable=True)
    api_id_obj = sqlalchemy.orm.relation("ApiId", foreign_keys=[api_id_fk])

    branch = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=False)
    commit_message = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=False)
    commit_sha = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=False)
    parent_commit_sha = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=True)
    on_default_branch = sqlalchemy.Column(sqlalchemy.Boolean)
    pull_request_id = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=True)
    pull_request_title = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=True)
    pull_request_body = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=True)
    tag = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=True)
    sender_username = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=True)
    sender_avatar_url = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=True)

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

    configuration_versions = sqlalchemy.orm.relation("ConfigurationVersion", back_populates="ingress_attribute")

    @classmethod
    def create(cls, authorised_repo, commit_sha, branch, pull_request_id, creator, tag):
        """Create new ingress attributes"""
        sender_username = authorised_repo.oauth_token.oauth_client.service_provider_instance.get_sender_username_for_commit(commit_sha)

        pull_request_title = None
        pull_request_body = None
        if pull_request_id:
            pull_request_title, pull_request_body = authorised_repo.oauth_token.oauth_client.service_provider_instance.get_pull_request_details(pull_request_id)

        ingress_attribute = cls(
            authorised_repo=authorised_repo,
            commit_sha=commit_sha,
            branch=branch,
            tag=tag,
            creator=creator,
            # Obtain additional attributes from authorised repo
            sender_username=sender_username,
            sender_avatar=authorised_repo.oauth_token.oauth_client.service_provider_instance.get_avatar_url_for_sender(sender_username),
            pull_request_id=pull_request_id,
            pull_request_title=pull_request_title,
            pull_request_body=pull_request_body
        )

        session = Database.get_session()
        session.add(ingress_attribute)
        session.commit()
        return ingress_attribute

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
        return self.authorised_repo.oauth_token.oauth_client.service_provider_instance.commit_url_template.format(commit_sha=self.commit_sha)

    @property
    def compare_url(self):
        """Return compare URL"""
        return self.authorised_repo.oauth_token.oauth_client.service_provider_instance.compare_url_template.format(
            commit_sha=self.commit_sha, parent_commit_sha=self.parent_commit_sha)

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
            self.sender_username)

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
                "sender-html-url": self.sender_html_url
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
                }
            },
            "links": {
                "self": f"/api/v2/ingress-attributes/{self.api_id}"
            }
        }