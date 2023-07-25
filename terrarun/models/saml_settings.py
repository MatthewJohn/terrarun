
from re import L
import sqlalchemy
from terrarun.api_error import ApiError

from terrarun.database import Base, Database
import terrarun.database
from terrarun.models.global_setting import GlobalSetting


class IdpCertificateMustBePresentError(ApiError):
    """IDP Certificate not provided."""

    pass


class SsoEndpointUrlMustBePresentError(ApiError):
    """SSO Endpoint URL not provided."""

    pass


class SloEndpointUrlMustBePresentError(ApiError):
    """SLO endpoint URL not provided."""

    pass


class SamlSettings(Base):

    __tablename__ = 'saml_settings'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    debug = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    old_idp_cert = sqlalchemy.Column(terrarun.database.Database.LargeString, default=None)
    idp_cert = sqlalchemy.Column(terrarun.database.Database.LargeString, default=None)
    slo_endpoint_url = sqlalchemy.Column(terrarun.database.Database.LargeString, default=None)
    sso_endpoint_url = sqlalchemy.Column(terrarun.database.Database.LargeString, default=None)
    attr_username = sqlalchemy.Column(terrarun.database.Database.LargeString, default=None)
    attr_groups = sqlalchemy.Column(terrarun.database.Database.LargeString, default=None)
    attr_site_admin = sqlalchemy.Column(terrarun.database.Database.LargeString, default=None)
    site_admin_role = sqlalchemy.Column(terrarun.database.Database.LargeString, default=None)
    sso_api_token_session_timeout = sqlalchemy.Column(sqlalchemy.Integer, default=None)
    acs_consumer_url = sqlalchemy.Column(terrarun.database.Database.LargeString, default=None)
    metadata_url = sqlalchemy.Column(terrarun.database.Database.LargeString, default=None)

    @classmethod
    def get_instance(cls):
        """Get instance of Saml settings"""
        session = Database.get_session()
        res = session.query(cls).first()
        if res is None:
            res = cls()
            session.add(res)
            session.commit()
        return res

    def update_attributes(self, entity):
        """Update SAML attributes from request attributes"""
        for attribute, value in entity.get_set_object_attributes().items():
            setattr(self, attribute, value)

        if self.enabled:
            if not self.idp_cert:
                raise IdpCertificateMustBePresentError(
                    "IDP certificate is required to enable SAML",
                    "An IDP certificate must be provided when enabling SAML",
                    pointer="/data/attributes/idp-cert"
                )
            if not self.slo_endpoint_url:
                raise SloEndpointUrlMustBePresentError(
                    "SLO endpoint is required to enable SAML",
                    "An SLO endpoint URL must be provided when enabling SAML",
                    pointer="/data/attributes/slo-endpoint-url"
                )
            if not self.sso_endpoint_url:
                raise SsoEndpointUrlMustBePresentError(
                    "SSO endpoint is required to enable SAML",
                    "An SSO endpoint URL must be provided when enabling SAML",
                    pointer="/data/attributes/sso-endpoint-url"
                )

        session = Database.get_session()
        session.add(self)
        session.commit()
