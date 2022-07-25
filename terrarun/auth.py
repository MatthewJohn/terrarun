
class Auth:
    """Provide interfaces to authenticate to system"""

    LOGIN_TOKEN = 'abcef-terrarun-abcdef1234567'

    def get_auth_token(self):
        """Return static token"""
        return self.LOGIN_TOKEN

    def get_user_account_by_auth_token(self, auth_token):
        """Return user by auth token."""
        if auth_token == Auth.LOGIN_TOKEN:
            return UserAccount(1)
        return None


class UserAccount:
    """User object."""

    def __init__(self, user_id):
        """Store user ID"""
        self._user_id = user_id

    def get_account_api_data(self):
        """Return API details for user"""
        return {
            "data": {
                "id": "user-V3R563qtJNcExAkN",
                "type": "users",
                "attributes": {
                "username": "admin",
                "is-service-account": False,
                "avatar-url": "https://www.gravatar.com/avatar/9babb00091b97b9ce9538c45807fd35f?s=100&d=mm",
                "v2-only": False,
                "is-site-admin": True,
                "is-sso-login": False,
                "email": "admin@hashicorp.com",
                "unconfirmed-email": None,
                "permissions": {
                    "can-create-organizations": True,
                    "can-change-email": True,
                    "can-change-username": True
                }
                },
                "relationships": {
                "authentication-tokens": {
                    "links": {
                        "related": "/api/v2/users/user-V3R563qtJNcExAkN/authentication-tokens"
                    }
                }
                },
                "links": {
                    "self": "/api/v2/users/user-V3R563qtJNcExAkN"
                }
            }
        }
