# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0


import datetime

import terrarun.models.organisation
import terrarun.models.user
import terrarun.workspace_execution_mode
import terrarun.models.plan
import terrarun.terraform_command
import terrarun.config

from .base_entity import (
    BaseEntity,
    NestedAttributes,
    EntityView,
    Attribute,
    ATTRIBUTED_REQUIRED,
)


class PlanExecutionDetailsEntity(NestedAttributes):
    """Entity for execution details for plan"""

    @classmethod
    def _get_attributes(cls):
        return (
            Attribute("agent-id", "agent_id", str, None, omit_undefined=True),
            Attribute("agent-name", "agent_name", str, None, omit_undefined=True),
            Attribute("agent-pool-id", "agent_pool_id", str, None, omit_undefined=True),
            Attribute("agent-pool-name", "agent_pool_name", str, None, omit_undefined=True),
            Attribute("mode", "mode", terrarun.workspace_execution_mode.WorkspaceExecutionMode, None, omit_none=True),
        )

    @classmethod
    def _from_object(cls, obj: 'terrarun.models.plan.Plan', effective_user: 'terrarun.models.user.User'):
        """Convert plan object agent details entity"""
        attributes = {
            "mode": obj.execution_mode
        }
        if obj.agent:
            attributes["agent_id"] = obj.agent.api_id
            attributes["agent_name"] = obj.agent.name
            attributes["agent_pool_id"] = obj.agent.agent_pool.api_id
            attributes["agent_pool_name"] = obj.agent.agent_pool.name
        return cls(attributes=attributes)


class PlanStatusTimestampsEntity(NestedAttributes):
    """Plan execution defailts entity"""

    @classmethod
    def _get_attributes(cls):
        return (
            Attribute("queued-at", "queued_at", datetime.datetime, None, omit_none=True),
            Attribute("started-at", "started_at", datetime.datetime, None, omit_none=True),
            Attribute("finished-at", "finished_at", datetime.datetime, None, omit_none=True),
        )

    @classmethod
    def _from_object(cls, obj: 'terrarun.models.plan.Plan', effective_user: 'terrarun.models.user.User'):
        """Convert plan object to status timestamps entity"""
        timestamps = obj.get_status_change_timestamps()
        print(timestamps)
        print(obj.status_timestamps)
        return cls(
            attributes={
                'queued_at': timestamps.get(terrarun.terraform_command.TerraformCommandState.QUEUED),
                'started_at': timestamps.get(terrarun.terraform_command.TerraformCommandState.RUNNING),
                # Obtain finished status and fallback to errored status
                'finished_at': timestamps.get(
                    terrarun.terraform_command.TerraformCommandState.FINISHED,
                    timestamps.get(terrarun.terraform_command.TerraformCommandState.ERRORED)
                ),
            }
        )


class PlanEntity(BaseEntity):

    type = "plans"

    @classmethod
    def _get_attributes(cls):
        return (
            Attribute("has-changes", "has_changes", bool, ATTRIBUTED_REQUIRED),
            Attribute("resource-additions", "resource_additions", int, ATTRIBUTED_REQUIRED),
            Attribute("resource-changes", "resource_changes", int, ATTRIBUTED_REQUIRED),
            Attribute("resource-destructions", "resource_destructions", int, ATTRIBUTED_REQUIRED),
            Attribute("status", "status", terrarun.terraform_command.TerraformCommandState, ATTRIBUTED_REQUIRED),
            Attribute("log-read-url", "log_read_url", str, ATTRIBUTED_REQUIRED),
            Attribute("execution-details", "execution_details", PlanExecutionDetailsEntity, ATTRIBUTED_REQUIRED),
            Attribute("status-timestamps", "status_timestamps", PlanStatusTimestampsEntity, ATTRIBUTED_REQUIRED),
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
                "execution_details": PlanExecutionDetailsEntity.from_object(obj=obj, effective_user=effective_user),
                "status_timestamps": PlanStatusTimestampsEntity.from_object(obj=obj, effective_user=effective_user),
            }
        )


class PlanView(PlanEntity, EntityView):

    pass
