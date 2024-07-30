# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0


import datetime

import terrarun.models.organisation
import terrarun.models.user
import terrarun.workspace_execution_mode
import terrarun.models.apply
import terrarun.terraform_command
import terrarun.config

from .base_entity import (
    BaseEntity,
    NestedAttributes,
    EntityView,
    Attribute,
    ATTRIBUTED_REQUIRED,
)
from .agent_execution_details import AgentExecutionDetailsEntity
from .execution_status_timestamps import ExecutionStatusTimestampsEntity


class ApplyEntity(BaseEntity):

    type = "applies"

    @classmethod
    def _get_attributes(cls):
        return (
            Attribute("resource-additions", "resource_additions", int, ATTRIBUTED_REQUIRED),
            Attribute("resource-changes", "resource_changes", int, ATTRIBUTED_REQUIRED),
            Attribute("resource-destructions", "resource_destructions", int, ATTRIBUTED_REQUIRED),
            Attribute("status", "status", terrarun.terraform_command.TerraformCommandState, ATTRIBUTED_REQUIRED),
            Attribute("log-read-url", "log_read_url", str, ATTRIBUTED_REQUIRED),
            Attribute("execution-details", "execution_details", AgentExecutionDetailsEntity, ATTRIBUTED_REQUIRED),
            Attribute("status-timestamps", "status_timestamps", ExecutionStatusTimestampsEntity, ATTRIBUTED_REQUIRED),
        )

    @classmethod
    def _from_object(cls, obj: 'terrarun.models.apply.Apply', effective_user: 'terrarun.models.user.User'):
        """Convert object to saml settings entity"""
        return cls(
            id=obj.api_id,
            attributes={
                "resource_additions": 0,
                "resource_changes": 0,
                "resource_destructions": 0,
                "status": obj.status,
                "log_read_url": f"{terrarun.config.Config().BASE_URL}/api/v2/applies/{obj.api_id}/log",
                "execution_details": AgentExecutionDetailsEntity.from_object(obj=obj, effective_user=effective_user),
                "status_timestamps": ExecutionStatusTimestampsEntity.from_object(obj=obj, effective_user=effective_user),
            }
        )


class ApplyView(ApplyEntity, EntityView):

    pass
