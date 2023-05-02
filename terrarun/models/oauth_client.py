
from enum import Enum
import sqlalchemy
import sqlalchemy.orm

import terrarun.database
from terrarun.database import Base
from terrarun.models.base_object import BaseObject
import terrarun.utils


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


class OauthServiceGitlabEnterpriseEdition(BaseOauthServiceProvider):
    """Oauth service for Gitlab Enterprise Edition"""

    @property
    def display_name(self):
        """Return display name"""
        return "Gitlab Enterprise Edition"


class ServiceProviderFactory:

    @classmethod
    def get_by_service_provider_name(cls, service_provider):
        """Get service provider class based on service provider name"""
        if service_provider is OauthServiceProvider.GITLAB_ENTERPRISE_EDITION:
            return OauthServiceGitlabEnterpriseEdition
        
        raise Exception(f"Unsupported service provider: {service_provider.name}")


class OauthClient(Base, BaseObject):

    ID_PREFIX = 'oc'
    RESERVED_NAMES = []

    __tablename__ = 'oauth_client'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=sqlalchemy.sql.func.now())

    name = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=True)
    key = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=False)
    http_url = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=False)
    api_url = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=False)
    oauth_token_string = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=False)
    private_key = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=True)
    secret = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=False)
    rsa_public_key = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=True)
    service_provider = sqlalchemy.Column(sqlalchemy.Enum(OauthServiceProvider), nullable=False)
    callback_id = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=False, unique=True)

    organisation_id = sqlalchemy.Column(sqlalchemy.ForeignKey(
        "organisation.id", name="fk_openid_client_organisation_id_organisation_id"),
        nullable=False
    )
    organisation = sqlalchemy.orm.relationship("Organisation", back_populates="oauth_clients")

    @property
    def service_provider_instance(self):
        """Return instance of service provider"""
        return ServiceProviderFactory.get_by_service_provider_name(self.service_provider)(self)

    def get_api_details(self):
        """Return API details for oauth client"""
        return {
            "id": self.api_id,
            "type": "oauth-clients",
            "attributes": {
                "created-at": terrarun.utils.datetime_to_json(self.created_at),
                "callback-url": f"https://app.terraform.io/auth/{self.callback_id}/callback",
                "connect-path": f"/auth/{self.callback_id}?organization_id={self.organisation.api_id}",
                "service-provider": self.service_provider,
                "service-provider-display-name": self.service_provider_instance.display_name,
                "name": self.name,
                "http-url": self.http_url,
                "api-url": self.api_url,
                "key": self.key,
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
                    "data": [],
                    "links": {
                        "related": "/api/v2/oauth-tokens/ot-KaeqH4cy72VPXFQT"
                    }
                }
            }   
        }