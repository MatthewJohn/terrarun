class Organisation:

    @classmethod
    def get_by_name(cls, organisation_name):
        """Return organisation object by name of organisation"""
        # Return fake organisation
        return Organisation(1)

    def __init__(self, organisation_id):
        """Store member variables."""
        self._organisation_id = organisation_id
    
    def get_entitlement_set_api(self):
        """Return API response for organisation entitlement"""
        return {
            "data": {
                "id": "org-Bzyc2JuegvVLAibn",
                "type": "entitlement-sets",
                "attributes": {
                    "cost-estimation": False,
                    "configuration-designer": True,
                    "operations": True,
                    "private-module-registry": False,
                    "sentinel": False,
                    "run-tasks": False,
                    "state-storage": False,
                    "teams": False,
                    "vcs-integrations": False,
                    "usage-reporting": False,
                    "user-limit": 5,
                    "self-serve-billing": True,
                    "audit-logging": False,
                    "agents": False,
                    "sso": False
                },
                "links": {
                    "self": "/api/v2/entitlement-sets/org-Bzyc2JuegvVLAibn"
                }
            }
        }