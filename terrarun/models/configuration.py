# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import os
import subprocess
from enum import Enum
from tarfile import TarFile
from tempfile import NamedTemporaryFile, TemporaryDirectory, TemporaryFile

import sqlalchemy
import sqlalchemy.orm
from terrarun.api_request import ApiRequest

from terrarun.models.base_object import BaseObject
from terrarun.database import Base, Database
from terrarun.models.blob import Blob
from terrarun.models.ingress_attribute import IngressAttribute
from terrarun.object_storage import ObjectStorage


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
    api_id_fk = sqlalchemy.Column(sqlalchemy.ForeignKey("api_id.id"), nullable=True)
    api_id_obj = sqlalchemy.orm.relation("ApiId", foreign_keys=[api_id_fk])

    workspace_id = sqlalchemy.Column(sqlalchemy.ForeignKey("workspace.id"), nullable=False)
    workspace = sqlalchemy.orm.relationship("Workspace", back_populates="configuration_versions")

    configuration_blob_id = sqlalchemy.Column(sqlalchemy.ForeignKey("blob.id"), nullable=True)
    configuration_blob = sqlalchemy.orm.relation("Blob", foreign_keys=[configuration_blob_id])

    runs = sqlalchemy.orm.relation("Run", back_populates="configuration_version")

    speculative = sqlalchemy.Column(sqlalchemy.Boolean)
    auto_queue_runs = sqlalchemy.Column(sqlalchemy.Boolean)
    status = sqlalchemy.Column(sqlalchemy.Enum(ConfigurationVersionStatus))

    ingress_attribute_id = sqlalchemy.Column(sqlalchemy.ForeignKey("ingress_attribute.id", name="configuration_version_ingress_attribute_id"), nullable=True)
    ingress_attribute = sqlalchemy.orm.relationship("IngressAttribute", back_populates="configuration_versions", foreign_keys=[ingress_attribute_id])

    @classmethod
    def create(cls, workspace, auto_queue_runs=True, speculative=False, ingress_attribute=None):
        """Create configuration and return instance."""
        cv = ConfigurationVersion(
            workspace=workspace,
            speculative=speculative,
            auto_queue_runs=auto_queue_runs,
            ingress_attribute=ingress_attribute,
            status=ConfigurationVersionStatus.PENDING
        )
        session = Database.get_session()
        session.add(cv)
        session.commit()

        if cv.auto_queue_runs:
            cv.queue()
        return cv

    @classmethod
    def generate_from_vcs(cls, workspace, speculative, commit_ref=None, branch=None, user=None, tag=None):
        """Create configuration version from VCS"""
        service_provider = workspace.authorised_repo.oauth_token.oauth_client.service_provider_instance

        if commit_ref is None:
            # Obtain branch from workspace,
            # if not specified
            if branch is None:
                branch = workspace.get_branch()
            if not branch:
                return None

            commit_ref = service_provider.get_latest_commit_ref(
                authorised_repo=workspace.authorised_repo, branch=branch
            )
        if commit_ref is None:
            return None

        # Determine if an ingress attributes object exists, if not, create one
        ingress_attributes = IngressAttribute.get_by_authorised_repo_and_commit_sha(
            authorised_repo=workspace.authorised_repo,
            commit_sha=commit_ref
        )

        if not ingress_attributes:
            ingress_attributes = IngressAttribute.create(
                authorised_repo=workspace.authorised_repo,
                commit_sha=commit_ref,
                branch=branch,
                creator=user,
                tag=tag,
                # @TODO Provide this whislt implementing
                # PR triggers
                pull_request_id=None
            )

        archive_data = service_provider.get_targz_by_commit_ref(
            authorised_repo=workspace.authorised_repo, commit_ref=commit_ref
        )
        if archive_data is None:
            return None

        configuration_version = cls.create(
            workspace=workspace,
            auto_queue_runs=True,
            speculative=speculative,
            ingress_attribute=ingress_attributes
        )
        configuration_version.process_upload(archive_data)
        return configuration_version

    @classmethod
    def get_configuration_version_by_git_commit_sha(cls, workspace, git_commit_sha):
        """Return configuration versions by workspace and git commit sha"""
        session = Database.get_session()
        return session.query(cls).join(
            IngressAttribute
        ).filter(
            cls.workspace==workspace,
            IngressAttribute.commit_sha==git_commit_sha
        ).all()

    @property
    def plan_only(self):
        """Return whether only a plan."""
        return False

    @property
    def storage_key(self):
        """Return object storage key"""
        return f"configuration-version/{self.api_id}.tgz"

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

        # Upload configuration version to s3
        self.update_to_object_storage(data=data)

        # Create blob for configuration version
        session = Database.get_session()
        blob = Blob(data=data)
        session.refresh(self)
        session.add(blob)
        self.configuration_blob = blob
        session.add(self)
        session.commit()

        self.update_status(ConfigurationVersionStatus.UPLOADED)

    def update_to_object_storage(self, data):
        """Upload to object storage"""
        object_storage = ObjectStorage()
        object_storage.upload_file(path=self.storage_key, content=data)

    def get_download_url(self):
        """Get pre-signed download URL for conifiguration archive"""
        object_storage = ObjectStorage()
        return object_storage.create_presigned_download_url(path=self.storage_key)

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

    def get_api_details(self, api_request: ApiRequest=None):
        """Return API details."""

        if api_request and \
                api_request.has_include(ApiRequest.Includes.CONFIGURATION_VERSION_INGRESS_ATTRIBUTES) and \
                self.ingress_attribute:
            api_request.add_included(self.ingress_attribute.get_api_details())

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
                            "id": self.ingress_attribute.api_id,
                            "type": "ingress-attributes"
                        },
                        "links": {
                            "related":
                            f"/api/v2/configuration-versions/{self.api_id}/ingress-attributes"
                        }
                    } if self.ingress_attribute else {}
                },
                "links": {
                    "self": f"/api/v2/configuration-versions/{self.api_id}",
                    "download": f"/api/v2/configuration-versions/{self.api_id}/download"
                }
            }
        }