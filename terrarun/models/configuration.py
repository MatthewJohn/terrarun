# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

import os
from enum import Enum
from typing import Optional
from tarfile import TarFile
from tempfile import NamedTemporaryFile, TemporaryDirectory

import sqlalchemy
import sqlalchemy.orm
from terrarun.api_error import ApiError
from terrarun.api_request import ApiRequest
from terrarun.logger import get_logger

from terrarun.models.base_object import BaseObject
from terrarun.database import Base, Database
from terrarun.models.blob import Blob
from terrarun.models.ingress_attribute import IngressAttribute
import terrarun.models.run
import terrarun.models.run_flow
import terrarun.models.workspace
from terrarun.object_storage import ObjectStorage
import terrarun.presign
import terrarun.models.user
import terrarun.models.run_queue
import terrarun.auth_context


logger = get_logger(__name__)


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
    api_id_obj = sqlalchemy.orm.relationship("ApiId", foreign_keys=[api_id_fk])

    workspace_id: int = sqlalchemy.Column(sqlalchemy.ForeignKey("workspace.id"), nullable=False)
    workspace: 'terrarun.models.workspace.Workspace' = sqlalchemy.orm.relationship("Workspace", back_populates="configuration_versions")

    configuration_blob_id = sqlalchemy.Column(sqlalchemy.ForeignKey("blob.id"), nullable=True)
    configuration_blob = sqlalchemy.orm.relationship("Blob", foreign_keys=[configuration_blob_id])

    runs = sqlalchemy.orm.relationship("Run", back_populates="configuration_version")

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
        return self.speculative

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

    def can_create_run(self, speculative):
        """Whether a run can be created for the configuration version"""
        logger.debug(self.api_id)

        # Check if configuration version doesn't contain ingress attributes
        if self.ingress_attribute is None:
            logger.debug("Allowing run - configuration version does not contain ingress attributes.")
            return True

        if self.speculative or speculative:
            logger.debug("Allowing run - configuration version is speculative")
            return True

        # Get environment group
        lifecycle = self.workspace.project.lifecycle
        environment = self.workspace.environment
        lifecycle_environment_group = None

        # @TODO Consider switching to iterating through lifecycle's environment groups and lifecycle_environments
        for lifecycle_environment in environment.lifecycle_environments:
            if lifecycle_environment.lifecycle_environment_group.lifecycle.id == lifecycle.id:
                lifecycle_environment_group = lifecycle_environment.lifecycle_environment_group
                break
        if lifecycle_environment_group is None:
            raise Exception("Could not find lifecycle group for workspace environment")
        
        # Check if lifecycle group order is 0 and allow
        if lifecycle_environment_group.order == 0:
            logger.debug("Allowing run - lifecycle_environment_group order is 0.")
            return True
        
        # Get parent lifecycle group
        parent_environment_lifecycle_group = None
        for lifecycle_environment_group_itx in lifecycle.lifecycle_environment_groups:
            if lifecycle_environment_group_itx.order == (lifecycle_environment_group.order - 1):
                parent_environment_lifecycle_group = lifecycle_environment_group_itx
        if parent_environment_lifecycle_group is None:
            raise Exception("Could not find parent lifecycle environment group for workspace lifecycle")

        # Get all runs in parent lifecycle group and
        # determine success counts per environment.
        run_count = 0
        successful_plan_count = 0
        successful_apply_count = 0
        parent_environment_count = 0
        for parent_lifecycle_environment in parent_environment_lifecycle_group.lifecycle_environments:
            parent_environment_count += 1

            # Get all runs in enviroment relating to the ingress attribute
            workspace_itx = self.workspace.project.get_workspace_for_environment(parent_lifecycle_environment.environment)
            if not workspace_itx:
                raise Exception(f"Could not find workspace in project ({self.workspace.project.name}) for environment ({parent_lifecycle_environment.environment.name})")

            runs = workspace_itx.get_runs_by_ingress_attribute(self.ingress_attribute)

            # Aggregate information for all runs for the workspace against
            # this ingress attribute
            run_found = False
            successful_plan_found = False
            successful_apply_found = False
            for run in runs:
                run_found = True
                # Check for any statuses that indicate that plan has completed successfully
                if run.status in [
                        terrarun.models.run_flow.RunStatus.PLANNED_AND_FINISHED, terrarun.models.run_flow.RunStatus.PLANNED,
                        terrarun.models.run_flow.RunStatus.APPLY_QUEUED, terrarun.models.run_flow.RunStatus.APPLYING,
                        terrarun.models.run_flow.RunStatus.PRE_APPLY_RUNNING, terrarun.models.run_flow.RunStatus.PRE_APPLY_COMPLETED,
                        terrarun.models.run_flow.RunStatus.POST_PLAN_RUNNING, terrarun.models.run_flow.RunStatus.POST_PLAN_COMPLETED]:
                    successful_plan_found = True

                # Check for states that indicate that apply has completed successfully
                if run.status in [terrarun.models.run_flow.RunStatus.APPLIED]:
                    successful_plan_found = True
                    successful_apply_found = True

            # Add count and successes to overalls for the environment group
            if run_found:
                run_count += 1
            if successful_plan_found:
                successful_plan_count += 1
            if successful_apply_found:
                successful_apply_count += 1

        # Check minimum runs, plans and applies against lifecyle group rules
        minimum_runs = parent_environment_lifecycle_group.minimum_runs if parent_environment_lifecycle_group.minimum_runs is not None else parent_environment_count
        if minimum_runs > run_count:
            logger.debug(f"Disallowing run - required runs in parent required: {minimum_runs}. Found: {run_count}")
            return ApiError(
                "Run could not be created",
                f"Lifecycle Environment Group ({', '.join([le.environment.name for le in parent_environment_lifecycle_group.lifecycle_environments])}) does not have enough runs for this version (required: {minimum_runs}, actual: {run_count})",
                pointer="/relationships/configuration-versions/data/id"
            )

        minimum_successful_plans = parent_environment_lifecycle_group.minimum_successful_plans if parent_environment_lifecycle_group.minimum_successful_plans is not None else parent_environment_count
        if minimum_successful_plans > successful_plan_count:
            logger.debug(f"Disallowing run - successful plans in parent required: {minimum_successful_plans}. Found: {successful_plan_count}")
            return ApiError(
                "Run could not be created",
                f"Lifecycle Environment Group ({', '.join([le.environment.name for le in parent_environment_lifecycle_group.lifecycle_environments])}) does not have enough successful plans for this version (required: {minimum_successful_plans}, actual: {successful_plan_count})",
                pointer="/relationships/configuration-versions/data/id"
            )

        minimum_successful_applies = parent_environment_lifecycle_group.minimum_successful_applies if parent_environment_lifecycle_group.minimum_successful_applies is not None else parent_environment_count
        if minimum_successful_applies > successful_apply_count:
            logger.debug(f"Disallowing run - successful applies in parent required: {minimum_successful_applies}. Found: {successful_apply_count}")
            return ApiError(
                "Run could not be created",
                f"Lifecycle Environment Group ({', '.join([le.environment.name for le in parent_environment_lifecycle_group.lifecycle_environments])}) does not have enough successful applies for this version (required: {minimum_successful_applies}, actual: {successful_apply_count})",
                pointer="/relationships/configuration-versions/data/id"
            )

        # Allow run
        return True

    def get_upload_url(self, auth_context: 'terrarun.auth_context.AuthContext'):
        """Return URL for terraform to upload configuration."""
        
        upload_path = f'/api/v2/upload-configuration/{self.api_id}'

        url_generator = terrarun.presign.PresignedUrlGenerator()
        return url_generator.create_url(auth_context=auth_context, path=upload_path)

    def get_api_details(self, auth_context: 'terrarun.auth_context.AuthContext', api_request: Optional[ApiRequest] = None):
        """Return API details."""

        if api_request and \
                api_request.has_include(ApiRequest.Includes.CONFIGURATION_VERSION_INGRESS_ATTRIBUTES) and \
                self.ingress_attribute:
            api_request.add_included(self.ingress_attribute.get_api_details())

        return {
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
                "upload-url": self.get_upload_url(auth_context=auth_context)
            },
            "relationships": {
                "ingress-attributes": {
                    "data": {
                        "id": self.ingress_attribute.api_id,
                        "type": "ingress-attributes"
                    } if self.ingress_attribute else None,
                    "links": {
                        "related": f"/api/v2/configuration-versions/{self.api_id}/ingress-attributes"
                    }
                },

                # Custom relationship
                "workspace": {
                    "data": {
                        "id": self.workspace.api_id,
                        "type": "workspaces"
                    }
                }
            },
            "links": {
                "self": f"/api/v2/configuration-versions/{self.api_id}",
                "download": f"/api/v2/configuration-versions/{self.api_id}/download"
            }
        }