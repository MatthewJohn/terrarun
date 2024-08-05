# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0


from datetime import datetime
from typing import Tuple, List, Optional

import terrarun.models.state_version
import terrarun.models.user
import terrarun.models.state_version_output
import terrarun.auth_context

from .base_entity import (
    ATTRIBUTED_REQUIRED,
    Attribute,
    BaseEntity,
    DataRelationshipView,
    ListRelationshipView,
    EntityView,
)


class StateVersionsOutputRelationship(DataRelationshipView):

    TYPE = "state-version-outputs"

    @classmethod
    def get_id_from_object(cls, obj: 'terrarun.models.state_version_output.StateVersionOutput') -> Optional[str]:
        """Get state version ID"""
        return obj.api_id


class StateVersionOutputListRelationship(ListRelationshipView):

    ENTITY_CLASS = StateVersionsOutputRelationship

    @classmethod
    def _get_objects(cls, obj: 'terrarun.models.state_version.StateVersion') -> List['terrarun.models.state_version.StateVersion']:
        """Return state versions"""
        return obj.state_version_outputs


class RunRelationship(DataRelationshipView):

    TYPE = "runs"

    @classmethod
    def get_id_from_object(cls, obj: 'terrarun.models.state_version.StateVersion') -> str:
        """Return ID"""
        if run := obj.run:
            return run.api_id


class CreatedByRelationship(DataRelationshipView):

    TYPE = "users"

    @classmethod
    def get_id_from_object(cls, obj: 'terrarun.models.state_version.StateVersion') -> str:
        """Return ID"""
        if user := obj.created_by:
            return user.api_id


class WorkspaceRelationship(DataRelationshipView):

    TYPE = "workspaces"

    @classmethod
    def get_id_from_object(cls, obj: 'terrarun.models.state_version.StateVersion') -> str:
        """Return ID"""
        return obj.workspace.api_id


class StateVersionEntity(BaseEntity):
    """Entity for state version"""

    type = "state-versions"

    RELATIONSHIPS = {
        "outputs": StateVersionOutputListRelationship,
        "run": RunRelationship,
        "workspace": WorkspaceRelationship,
        "created-by": CreatedByRelationship,
    }

    @classmethod
    def _get_attributes(cls) -> Tuple[Attribute]:
        return (
            Attribute("created-at", "created_at", datetime, ATTRIBUTED_REQUIRED),
            Attribute("size", "size", int, None),
            Attribute("hosted-state-download-url", "hosted_state_download_url", str, None),
            Attribute("hosted-json-state-download-url", "hosted_json_state_download_url", str, None),
            Attribute("hosted-state-upload-url", "hosted_state_upload_url", str, None),
            Attribute("hosted-json-state-upload-url", "hosted_json_state_upload_url", str, None),
            # Attribute("modules", "modules", bool, False),
            # Attribute("proviers", "providers", str, None),
            # Attribute("resources", "resources", bool, None),
            Attribute("resources-processed", "resources_processed", bool, False),
            Attribute("serial", "serial", int, ATTRIBUTED_REQUIRED),
            Attribute("state-version", "state_version", int, None),
            Attribute("status", "status", terrarun.models.state_version.StateVersionStatus, None),
            Attribute("terraform-version", "terraform_version", str, None),
            Attribute("vcs-commit-url", "vcs_commit_url", str, None),
            Attribute("vcs-commit-sha", "vcs_commit_sha", str, None),
        )

    @classmethod
    def _from_object(cls, obj: 'terrarun.models.state_version.StateVersion', auth_context: 'terrarun.auth_context.AuthContext'):
        """Convert object to saml settings entity"""
        return cls(
            id=obj.api_id,
            attributes={
                "created_at": obj.created_at,
                "size": 940,
                "hosted_state_download_url": obj.get_state_download_url(auth_context=auth_context),
                "hosted_json_state_download_url": obj.get_json_state_download_url(auth_context=auth_context),
                "hosted_state_upload_url": obj.get_state_upload_url(auth_context=auth_context),
                "hosted_json_state_upload_url": obj.get_json_state_upload_url(auth_context=auth_context),
                "resources_processed": obj.resources_processed,
                "serial": obj.serial,
                "state_version": obj.state_version,
                "status": obj.status,
                "terraform_version": obj.terraform_version,
            },
        )


class StateVersionCreateEntity(StateVersionEntity):
    """Entity for creating state version"""

    RELATIONSHIPS = {
        "run": RunRelationship,
    }

    require_id = False
    include_attributes = [
        "serial",
        "md5",
        "state",
        "lineage",
        "json_state",
        "json_state_outputs",
        "force"
    ]

    @classmethod
    def _get_attributes(cls) -> Tuple[Attribute]:
        return super()._get_attributes() + (
            Attribute("md5", "md5", str, ATTRIBUTED_REQUIRED),
            Attribute("serial", "serial", str, ATTRIBUTED_REQUIRED),
            Attribute("lineage", "lineage", str, None),
            Attribute("json-state", "json_state", str, None),
            Attribute("json-state-outputs", "json_state_outputs", str, None),
            Attribute("force", "force", bool, False),
        )


class StateVersionView(StateVersionEntity, EntityView):

    pass
