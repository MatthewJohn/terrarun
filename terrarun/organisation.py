
from terrarun.workspace import Workspace


class Organisation:

    @classmethod
    def get_by_name(cls, organisation_name):
        """Return organisation object by name of organisation"""
        # Return fake organisation
        org = Organisation("org-Bzyc2JuegvVLAibn")
        org._name = organisation_name
        return org

    def __init__(self, id_):
        """Store member variables."""
        self._id = id_
        self._name = None
    
    def get_entitlement_set_api(self):
        """Return API response for organisation entitlement"""
        return {
            "data": {
                "id": self._id,
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
                    "self": f"/api/v2/entitlement-sets/{self._id}"
                }
            }
        }

    def get_workspace_by_name(self, workspace_name):
        """Return workspace object within organisation"""
        return Workspace(self, workspace_name)
