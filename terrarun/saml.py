
from terrarun.models.global_setting import GlobalSetting

class Saml:

    def __init__(self):
        """Load saml configuration"""
        self._enabled = GlobalSetting.get_setting("saml-enabled")
        self._debug = GlobalSetting.get_setting("saml-debug")
        self._old_idp_cert = GlobalSetting.get_setting("saml-old-idp-cert")
        self._idp_cert = GlobalSetting.get_setting("saml-idp-cert")
        self._slo_endpoint_url = GlobalSetting.get_setting("saml-slo-endpoint-url")
        self._sso_endpoint_url = GlobalSetting.get_setting("saml-sso-endpoint-url")
        self._attr_username = GlobalSetting.get_setting("saml-attr-username")
        self._attr_groups = GlobalSetting.get_setting("saml-attr-groups")
        self._attr_site_admin = GlobalSetting.get_setting("saml-attr-site-admin")
        self._site_admin_role = GlobalSetting.get_setting("saml-site-admin-role")
        self._sso_api_token_session_timeout = GlobalSetting.get_setting("saml-sso-api-token-session-timeout")
        self._acs_consumer_url = GlobalSetting.get_setting("saml-acs-consumer-url")
        self._metadata_url = GlobalSetting.get_setting("saml-metadata-url")

    @property
    def enabled(self):
        """Return enabled property"""
        return self._enabled

    @property
    def debug(self):
        """Return debug property"""
        return self._debug

    @property
    def old_idp_cert(self):
        """Return old_idp_cert property"""
        return self._old_idp_cert

    @property
    def idp_cert(self):
        """Return idp_cert property"""
        return self._idp_cert

    @property
    def slo_endpoint_url(self):
        """Return slo_endpoint_url property"""
        return self._slo_endpoint_url

    @property
    def sso_endpoint_url(self):
        """Return sso_endpoint_url property"""
        return self._sso_endpoint_url

    @property
    def attr_username(self):
        """Return attr_username property"""
        return self._attr_username

    @property
    def attr_groups(self):
        """Return attr_groups property"""
        return self._attr_groups

    @property
    def attr_site_admin(self):
        """Return attr_site_admin property"""
        return self._attr_site_admin

    @property
    def site_admin_role(self):
        """Return site_admin_role property"""
        return self._site_admin_role

    @property
    def sso_api_token_session_timeout(self):
        """Return sso_api_token_session_timeout property"""
        return self._sso_api_token_session_timeout

    @property
    def acs_consumer_url(self):
        """Return acs_consumer_url property"""
        return self._acs_consumer_url

    @property
    def metadata_url(self):
        """Return metadata_url property"""
        return self._metadata_url

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

