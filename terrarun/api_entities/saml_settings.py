
from terrarun.models.saml_settings import SamlSettings as SamlSettingsModel

from .base_entity import BaseEntity, EntityView, Attribute, ATTRIBUTED_REQUIRED


class SamlSettingsEntity(BaseEntity):

    type = "saml-settings"

    attributes = (
        Attribute("enabled", "enabled", bool, False),
        Attribute("debug", "debug", bool, False),
        Attribute("old-idp-cert", "old_idp_cert", str, None),
        Attribute("idp-cert", "idp_cert", str, None),
        Attribute("slo-endpoint-url", "slo_endpoint_url", str, None),
        Attribute("sso-endpoint-url", "sso_endpoint_url", str, None),
        Attribute("attr-username", "attr_username", str, "Username"),
        Attribute("attr-groups", "attr_groups", str, "MemberOf"),
        Attribute("attr-site-admin", "attr_site_admin", str, "SiteAdmin"),
        Attribute("site-admin-role", "site_admin_role", str, "site-admins"),
        Attribute("sso-api-token-session-timeout", "sso_api_token_session_timeout", int, 1209600),
        Attribute("acs-consumer-url", "acs_consumer_url", str, ""),
        Attribute("metadata-url", "metadata_url", str, "")
    )

    def __init__(self, id,
                 enabled, debug,
                 old_idp_cert, idp_cert,
                 slo_endpoint_url, sso_endpoint_url,
                 attr_username, attr_groups,
                 attr_site_admin, site_admin_role,
                 sso_api_token_session_timeout,
                 acs_consumer_url, metadata_url):
        """Store member variables"""
        super().__init__()
        self.id = id
        self.enabled = enabled
        self.debug = debug
        self.old_idp_cert = old_idp_cert
        self.idp_cert = idp_cert
        self.slo_endpoint_url = slo_endpoint_url
        self.sso_endpoint_url = sso_endpoint_url
        self.attr_username = attr_username
        self.attr_groups = attr_groups
        self.attr_site_admin = attr_site_admin
        self.site_admin_role = site_admin_role
        self.sso_api_token_session_timeout = sso_api_token_session_timeout
        self.acs_consumer_url = acs_consumer_url
        self.metadata_url = metadata_url

    def get_attributes(self):
        """Return saml provider attributes"""
        return {
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

    @classmethod
    def from_object(cls, obj: SamlSettingsModel):
        """Convert object to saml settings entity"""
        return cls(
            id="saml",
            enabled=obj.enabled,
            debug=obj.debug,
            old_idp_cert=obj.old_idp_cert,
            idp_cert=obj.idp_cert,
            slo_endpoint_url=obj.slo_endpoint_url,
            sso_endpoint_url=obj.sso_endpoint_url,
            attr_username=obj.attr_username,
            attr_groups=obj.attr_groups,
            attr_site_admin=obj.attr_site_admin,
            site_admin_role=obj.site_admin_role,
            sso_api_token_session_timeout=obj.sso_api_token_session_timeout,
            acs_consumer_url=obj.acs_consumer_url,
            metadata_url=obj.metadata_url
        )


class SamlSettingsView(SamlSettingsEntity, EntityView):
    """View for settings"""
    pass
