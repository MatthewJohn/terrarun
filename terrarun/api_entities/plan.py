# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0


from typing import Optional, List

import terrarun.models.organisation
import terrarun.models.user
import terrarun.workspace_execution_mode
import terrarun.models.plan
import terrarun.terraform_command
import terrarun.models.state_version
import terrarun.config

from .base_entity import (
    BaseEntity,
    DataRelationshipView,
    ListRelationshipView,
    EntityView,
    Attribute,
    ATTRIBUTED_REQUIRED,
)
from .agent_execution_details import AgentExecutionDetailsEntity
from .execution_status_timestamps import ExecutionStatusTimestampsEntity


class StateVersionsRelationship(DataRelationshipView):

    TYPE = "state-versions"

    @classmethod
    def get_id_from_object(cls, obj: 'terrarun.models.state_version.StateVersion') -> Optional[str]:
        """Get state version ID"""
        return obj.api_id


class StateVersionListRelationship(ListRelationshipView):

    ENTITY_CLASS = StateVersionsRelationship

    @classmethod
    def _get_objects(cls, obj: 'terrarun.models.plan.Plan') -> List['terrarun.models.state_version.StateVersion']:
        """Return state versions"""
        state_versions = []
        if obj.state_version:
            state_versions.append(obj.state_version)
        return state_versions


class PlanEntity(BaseEntity):

    type = "plans"

    RELATIONSHIPS = {
        "state-versions": StateVersionListRelationship,
    }

    @classmethod
    def _get_attributes(cls):
        return (
            Attribute("has-changes", "has_changes", bool, ATTRIBUTED_REQUIRED),
            Attribute("resource-additions", "resource_additions", int, ATTRIBUTED_REQUIRED),
            Attribute("resource-changes", "resource_changes", int, ATTRIBUTED_REQUIRED),
            Attribute("resource-destructions", "resource_destructions", int, ATTRIBUTED_REQUIRED),
            Attribute("status", "status", terrarun.terraform_command.TerraformCommandState, ATTRIBUTED_REQUIRED),
            Attribute("log-read-url", "log_read_url", str, ATTRIBUTED_REQUIRED),
            Attribute("execution-details", "execution_details", AgentExecutionDetailsEntity, ATTRIBUTED_REQUIRED),
            Attribute("status-timestamps", "status_timestamps", ExecutionStatusTimestampsEntity, ATTRIBUTED_REQUIRED),
        )

    @classmethod
    def _from_object(cls, obj: 'terrarun.models.plan.Plan', effective_user: 'terrarun.models.user.User'):
        """Convert object to saml settings entity"""
        return cls(
            id=obj.api_id,
            attributes={
                "has_changes": obj.has_changes,
                "resource_additions": obj.resource_additions,
                "resource_changes": obj.resource_changes,
                "resource_destructions": obj.resource_destructions,
                "status": obj.status,
                "log_read_url": f"{terrarun.config.Config().BASE_URL}/api/v2/plans/{obj.api_id}/log",
                "execution_details": AgentExecutionDetailsEntity.from_object(obj=obj, effective_user=effective_user),
                "status_timestamps": ExecutionStatusTimestampsEntity.from_object(obj=obj, effective_user=effective_user),
            }
        )


class PlanView(PlanEntity, EntityView):

    pass
