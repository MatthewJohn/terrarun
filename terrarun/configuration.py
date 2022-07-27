
import os
import subprocess
from enum import Enum
from tarfile import TarFile
from tempfile import NamedTemporaryFile, TemporaryDirectory, TemporaryFile

import sqlalchemy
import sqlalchemy.orm

from terrarun.base_object import BaseObject
from terrarun.database import Base, Database


class ConfigurationVersionStatus(Enum):

    PENDING = 'pending'
    FETCHING = 'fetching'
    UPLOADED = 'uploaded'
    ARCHIVED = 'archived'
    ERRORED = 'errored'


class ConfigurationVersion(Base, BaseObject):
    """Interface for uploaded configuration files"""

    __tablename__ = 'configuration_version'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    workspace_id = sqlalchemy.Column(sqlalchemy.ForeignKey("workspace.id"), nullable=False)
    workspace = sqlalchemy.orm.relationship("Workspace", back_populates="configuration_versions")

    speculative = sqlalchemy.Column(sqlalchemy.Boolean)
    auto_queue_runs = sqlalchemy.Column(sqlalchemy.Boolean)
    status = sqlalchemy.Column(sqlalchemy.Enum(ConfigurationVersionStatus))

    @classmethod
    def create(cls, workspace, auto_queue_runs=True, speculative=False):
        """Create configuration and return instance."""
        cv = ConfigurationVersion(workspace=workspace, speculative=speculative, auto_queue_runs=auto_queue_runs)
        with Database.get_session() as session:
            session.add(cv)
            session.commit()

        if cv.auto_queue_runs:
            cv.queue()
        return cv

    @property
    def plan_only(self):
        """Return whether only a plan."""
        return False

    def __init__(self, workspace, id_):
        """Store member variables."""
        self.speculative = False
        self._workspace = workspace
        self._id = id_
        self._extract_dir = None
        self._status = ConfigurationVersionStatus.PENDING

    def queue(self):
        """Queue."""
        self._status = ConfigurationVersionStatus.FETCHING

    def process_upload(self, data):
        """Handle upload of archive."""
        with NamedTemporaryFile(delete=False) as temp_file:
            tar_gz_file = temp_file.name

        try:
            with open(tar_gz_file, 'wb') as tar_gz_fh:
                tar_gz_fh.write(data)
                
            with TemporaryDirectory() as extract_dir:
                pass
            self._extract_dir = extract_dir
            os.mkdir(self._extract_dir)
            tar_file = TarFile.open(tar_gz_file, 'r')
            tar_file.extractall(self._extract_dir)

            # Create override file for reconfiguring backend
            with open(os.path.join(self._extract_dir, 'override.tf'), 'w') as override_fh:
                override_fh.write("""
terraform {
  backend "local" {
    path = "terraform.tfstate"
  }
}
""".strip())
        finally:
            os.unlink(tar_gz_file)
        self._status = ConfigurationVersionStatus.UPLOADED

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
                    "speculative": self.speculative,
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