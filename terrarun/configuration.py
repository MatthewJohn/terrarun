
from enum import Enum

class ConfigurationVersionStatus(Enum):

    PENDING = 'pending'
    FETCHING = 'fetching'
    UPLOADED = 'uploaded'
    ARCHIVED = 'archived'
    ERRORED = 'errored'


class ConfigurationVersion():
    """Interface for uploaded configuration files"""

    CONFIGURATIONS = {}

    @classmethod
    def create(cls, workspace):
        """Create configuration and return instance."""
        id_ = 'cv-ntv3HbhJqvFzam{id}'.format(id=str(len(cls.CONFIGURATIONS)).zfill(2))
        cv = ConfigurationVersion(workspace=workspace, id_=id_)
        cls.CONFIGURATIONS[id_] = cv
        return cv

    def __init__(self, workspace, id_):
        """Store member variables."""
        self._workspace = workspace
        self._id = id_
        self._status = ConfigurationVersionStatus.PENDING

    def get_upload_url(self):
        """Return URL for terraform to upload configuration."""
        return f'/api/v2/upload-configuration/{self._id}'

    def get_api_details(self):
        """Return API details."""
        return {
            "data": {
                "id": self._id,
                "type": "configuration-versions",
                "attributes": {
                    "auto-queue-runs": True,
                    "error": None,
                    "error-message": None,
                    "source": "tfe-api",
                    "speculative": False,
                    "status": self._status.value,
                    "status-timestamps": {},
                    "upload-url": self.get_upload_url()
                },
                "relationships": {
                    "ingress-attributes": {
                        "data": {
                            "id": "ia-i4MrTxmQXYxH2nYD",
                            "type": "ingress-attributes"
                        },
                        "links": {
                            "related":
                            f"/api/v2/configuration-versions/{self._id}/ingress-attributes"
                        }
                    }
                },
                "links": {
                    "self": f"/api/v2/configuration-versions/{self._id}",
                    "download": f"/api/v2/configuration-versions/{self._id}/download"
                }
            }
        }