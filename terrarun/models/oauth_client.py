
from enum import Enum
import secrets
import uuid
import urllib.parse

import sqlalchemy
import sqlalchemy.orm
from flask import redirect, make_response
import requests

import terrarun.database
from terrarun.database import Base, Database
from terrarun.models.base_object import BaseObject
from terrarun.models.github_app_oauth_token import GithubAppOauthToken
from terrarun.models.oauth_token import OauthToken
import terrarun.utils
import terrarun.config


class OauthServiceProvider(Enum):

    GITHUB = "github"
    GITHUB_ENTERPRISE = "github_enterprise"
    GITLAB_HOSTED = "gitlab_hosted"
    GITLAB_COMMUNITY_EDITION = "gitlab_community_edition"
    GITLAB_ENTERPRISE_EDITION = "gitlab_enterprise_edition"
    ADO_SERVER = "ado_server"


class BaseOauthServiceProvider:
    """"Base oauth service provider"""

    def __init__(self, oauth_client):
        """"Store memeber variables"""
        self._oauth_client = oauth_client

    @property
    def display_name(self):
        """Return display name"""
        raise NotImplementedError

    @property
    def state_cookie_key(self):
        """Return cookie key for state"""
        return f"{self._oauth_client.api_id}_authorize_state"

    @staticmethod
    def _generate_state_value():
        """Return random state value"""
        return secrets.token_urlsafe(15)

    def get_authorise_response_object(self):
        """Obtain redirect location and cookie to be set"""
        raise NotImplementedError

    def handle_authorise_callback(self, current_user, request, request_session):
        """Handle authorise callback"""
        raise NotImplementedError


class OauthServiceGitlabEnterpriseEdition(BaseOauthServiceProvider):
    """Oauth service for Gitlab Enterprise Edition"""

    @property
    def display_name(self):
        """Return display name"""
        return "Gitlab Enterprise Edition"


class OauthServiceGithub(BaseOauthServiceProvider):
    """Oauth service for Github hosted"""

    @property
    def display_name(self):
        """Return display name"""
        return "Github"

    def _user_current_username(self, token):
        """Get username for authenticated user"""
        res = requests.get(
            f"{self._oauth_client.api_url}/user",
            headers={
                "X-GitHub-Api-Version": "2022-11-28",
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json"
            }
        )

        if res.status_code != 200:
            return None

        return res.json().get("login", None)

    def get_authorise_response_object(self):
        """Obtain redirect location and cookie to be set"""
        state = self._generate_state_value()
        query_params = {
            'client_id': self._oauth_client.key,
            'response_type': 'code',
            'scope': 'user,repo,admin:repo_hook',
            'state': state,
            'redirect_uri': self._oauth_client.callback_url
        }

        url = f"{self._oauth_client.http_url}/login/oauth/authorize?{urllib.parse.urlencode(query_params)}"

        response_obj = make_response(redirect(url, code=302))
        session = {
            self.state_cookie_key: state
        }

        return response_obj, session

    def _generate_access_token(self, code):
        """Generate a github access token using temporary code"""
        res = requests.post(
            f"{self._oauth_client.http_url}/login/oauth/access_token",
            headers={
                "Accept": "application/json"
            },
            params={
                "client_id": self._oauth_client.key,
                "client_secret": self._oauth_client.secret,
                "code": code,
                "redirect_uri": self._oauth_client.callback_url
            }
        )

        # Check staus code of access token request
        if res.status_code != 200:
            return None

        # @TODO Check token_type and scope
        return res.json().get("access_token")

    def handle_authorise_callback(self, current_user, request, request_session):
        """Handle authorise callback"""
        request_args = request.args

        # Ensure state in request matches cookie
        state = request_args.get("state")
        cookie_state = request_session.get(self.state_cookie_key)
        if not state or not cookie_state or state != cookie_state:
            return None

        if not (code := request_args.get("code")):
            return None

        # Generate access token
        access_token = self._generate_access_token(code)
        if not access_token:
            return None

        if not (github_username := self._user_current_username(token=access_token)):
            return None

        return GithubAppOauthToken.create(
            oauth_client=self._oauth_client,
            user=current_user,
            token=access_token,
            github_username=github_username
        )


class ServiceProviderFactory:

    @classmethod
    def get_by_service_provider_name(cls, service_provider):
        """Get service provider class based on service provider name"""
        if service_provider is OauthServiceProvider.GITLAB_ENTERPRISE_EDITION:
            return OauthServiceGitlabEnterpriseEdition
        elif service_provider is OauthServiceProvider.GITHUB:
            return OauthServiceGithub
        raise Exception(f"Unsupported service provider: {service_provider.name}")


class OauthClient(Base, BaseObject):

    ID_PREFIX = 'oc'
    RESERVED_NAMES = []

    __tablename__ = 'oauth_client'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=sqlalchemy.sql.func.now())

    name = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=True)
    key = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=True)
    http_url = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=False)
    api_url = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=False)
    private_key = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=True)
    secret = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=True)
    rsa_public_key = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=True)
    service_provider = sqlalchemy.Column(sqlalchemy.Enum(OauthServiceProvider), nullable=False)
    callback_id = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=False, unique=True)

    organisation_id = sqlalchemy.Column(sqlalchemy.ForeignKey(
        "organisation.id", name="fk_openid_client_organisation_id_organisation_id"),
        nullable=False
    )
    organisation = sqlalchemy.orm.relationship("Organisation", back_populates="oauth_clients")

    oauth_tokens = sqlalchemy.orm.relation("OauthToken", back_populates="oauth_client")

    @classmethod
    def get_by_callback_uuid(cls, callback_uuid):
        """Return oauth client by callback uuid"""
        session = Database.get_session()
        return session.query(cls).where(cls.callback_id==callback_uuid).first()

    @classmethod
    def create(cls, organisation, name, service_provider, key, http_url, api_url, oauth_token_string, private_key, secret, rsa_public_key):
        """Create oauth client"""
        oauth_client = cls(
            service_provider=service_provider,
            organisation=organisation,
            name=name,
            key=key,
            http_url=http_url,
            api_url=api_url,
            private_key=private_key,
            secret=secret,
            rsa_public_key=rsa_public_key,
            callback_id=str(uuid.uuid4())
        )
        session = Database.get_session()
        session.add(oauth_client)

        # @TODO How should user for oauth token be handled?
        # if oauth_token_string:
        #     OauthToken.create(
        #         oauth_client=oauth_client,
        #         token=oauth_token_string,
        #         session=session
        #     )
        session.commit()
        return oauth_client

    def delete(self):
        """Mark object as deleted"""
        session = Database.get_session()
        # Delete any oauth tokens
        for oauth_token in self.oauth_tokens:
            oauth_token.delete()

        session.delete(self)
        session.commit()

    @property
    def service_provider_instance(self):
        """Return instance of service provider"""
        return ServiceProviderFactory.get_by_service_provider_name(self.service_provider)(self)

    @property
    def callback_url(self):
        """Return callback URL for oauth client"""
        return f"{terrarun.config.Config().BASE_URL}/auth/{self.callback_id}/callback"

    @property
    def connect_path(self):
        """Return connect path"""
        return f"/auth/{self.callback_id}?organization_id={self.organisation.api_id}"

    def get_relationship(self):
        """Return relationship data for oauth client."""
        return {
            "id": self.api_id,
            "type": "oauth-clients"
        }

    def get_api_details(self):
        """Return API details for oauth client"""
        return {
            "id": self.api_id,
            "type": "oauth-clients",
            "attributes": {
                "created-at": terrarun.utils.datetime_to_json(self.created_at),
                "callback-url": self.callback_url,
                "connect-path": self.connect_path,
                "service-provider": self.service_provider.value,
                "service-provider-display-name": self.service_provider_instance.display_name,
                "name": self.name,
                "http-url": self.http_url,
                "api-url": self.api_url,
                "key": self.key,
                # Never return the secret
                "secret": None,
                "rsa-public-key": self.rsa_public_key
            },
            "relationships": {
                "organization": {
                    "data": {
                        "id": self.organisation.name_id,
                        "type": "organizations"
                    },
                    "links": {
                        "related": f"/api/v2/organizations/{self.organisation.name_id}"
                    }
                },
                "oauth-tokens": {
                    "data": [
                        oauth_token.get_relationship()
                        for oauth_token in self.oauth_tokens
                    ],
                    "links": {
                        "related": f"/api/v2/oauth-clients/{self.api_id}/oauth-tokens"
                    }
                }
            }   
        }