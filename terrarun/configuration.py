
import os
import subprocess
from enum import Enum
from tarfile import TarFile
from tempfile import NamedTemporaryFile, TemporaryDirectory, TemporaryFile

import sqlalchemy
import sqlalchemy.orm

from terrarun.base_object import BaseObject
from terrarun.database import Base, Database
from terrarun.blob import Blob


class ConfigurationVersionStatus(Enum):

    PENDING = 'pending'
    FETCHING = 'fetching'
    UPLOADED = 'uploaded'
    ARCHIVED = 'archived'
    ERRORED = 'errored'


class ConfigurationVersion(Base, BaseObject):
    """Interface for uploaded configuration files"""

    ID_PREFIX = 'cv'

    __tablename__ = 'configuration_version'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    workspace_id = sqlalchemy.Column(sqlalchemy.ForeignKey("workspace.id"), nullable=False)
    workspace = sqlalchemy.orm.relationship("Workspace", back_populates="configuration_versions")

    configuration_blob_id = sqlalchemy.Column(sqlalchemy.ForeignKey("blob.id"), nullable=True)
    configuration_blob = sqlalchemy.orm.relation("Blob", foreign_keys=[configuration_blob_id])

    runs = sqlalchemy.orm.relation("Run", back_populates="configuration_version")

    speculative = sqlalchemy.Column(sqlalchemy.Boolean)
    auto_queue_runs = sqlalchemy.Column(sqlalchemy.Boolean)
    status = sqlalchemy.Column(sqlalchemy.Enum(ConfigurationVersionStatus))

    @classmethod
    def create(cls, workspace, auto_queue_runs=True, speculative=False):
        """Create configuration and return instance."""
        cv = ConfigurationVersion(
            workspace=workspace,
            speculative=speculative,
            auto_queue_runs=auto_queue_runs,
            status=ConfigurationVersionStatus.PENDING
        )
        session = Database.get_session()
        session.add(cv)
        session.commit()

        if cv.auto_queue_runs:
            cv.queue()
        return cv

    @property
    def plan_only(self):
        """Return whether only a plan."""
        return False

    def __init__(self, *args, **kwargs):
        """Store member variables."""
        super(ConfigurationVersion, self).__init__(*args, **kwargs)
        self._extract_dir = None

    def update_status(self, new_status):
        """Update state of configuration version."""
        session = Database.get_session()
        session.refresh(self)
        self.status = new_status
        session.add(self)
        session.commit()

    def queue(self):
        """Queue."""
        self.update_status(ConfigurationVersionStatus.FETCHING)

    def process_upload(self, data):
        """Handle upload of archive."""
        if self.configuration_blob:
            raise Exception('Configuration version already uploaded')

        # Create blob for configuration version
        session = Database.get_session()
        blob = Blob(data=data)
        session.add(blob)
        session.commit()

        self.update_status(ConfigurationVersionStatus.UPLOADED)

    def extract_configuration(self):
        if not self.configuration_blob:
            raise Exception('Configuration version not uploaded')

        data = self.configuration_blob.data
        with NamedTemporaryFile(delete=False) as temp_file:
            tar_gz_file = temp_file.name

        try:
            with open(tar_gz_file, 'wb') as tar_gz_fh:
                tar_gz_fh.write(data)
                
            with TemporaryDirectory() as extract_dir:
                pass
            os.mkdir(extract_dir)
            tar_file = TarFile.open(tar_gz_file, 'r')
            tar_file.extractall(extract_dir)

            # Create override file for reconfiguring backend
            with open(os.path.join(extract_dir, 'override.tf'), 'w') as override_fh:
                override_fh.write("""
terraform {
  backend "local" {
    path = "terraform.tfstate"
  }
}
""".strip())
        finally:
            os.unlink(tar_gz_file)
        return extract_dir

    def get_upload_url(self):
        """Return URL for terraform to upload configuration."""
        return f'/api/v2/upload-configuration/{self.api_id}'

    def get_api_details(self):
        """Return API details."""
        return {
            "data": {
                "id": self.api_id,
                "type": "configuration-versions",
                "attributes": {
                    "auto-queue-runs": True,
                    "error": None,
                    "error-message": None,
                    "source": "tfe-api",
                    "speculative": self.speculative,
                    "status": self.status.value,
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
                            f"/api/v2/configuration-versions/{self.api_id}/ingress-attributes"
                        }
                    }
                },
                "links": {
                    "self": f"/api/v2/configuration-versions/{self.api_id}",
                    "download": f"/api/v2/configuration-versions/{self.api_id}/download"
                }
            }
        }