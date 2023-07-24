
import sqlalchemy

from terrarun.database import Base, Database
import terrarun.database
from terrarun.models.global_setting import GlobalSetting


class SamlSettings(Base):

    __tablename__ = 'saml_settings'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    debug = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    debug = sqlalchemy.Column(terrarun.database.Database.LargeString, default=None)
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

    def update_from_request_attributes(self, attributes, api_request):
        """Update SAML attributes from request attributes"""
        if "enabled" not in attributes:
            pass

    def get_api_details(self):
        """Return API request details"""
        return {
            "id": "saml",
            "type": "saml-settings",
            "attributes": {
                "enabled": self.enabled,
                "debug": self.debug,
                "old-idp-cert": self.old_idp_cert,
                "idp-cert": self.idp_cert,
                "slo-endpoint-url": self.slo_endpoint_url,
                "sso-endpoint-url": self.sso_endpoint_url,
                "attr-username": self.attr_username,
                "attr-groups": self.attr_groups,
                "attr-site-admin": self.attr_site_admin,
                "site-admin-role": self.site_admin_role,
                "sso-api-token-session-timeout": self.sso_api_token_session_timeout,
                "acs-consumer-url": self.acs_consumer_url,
                "metadata-url": self.metadata_url
            }
        }

