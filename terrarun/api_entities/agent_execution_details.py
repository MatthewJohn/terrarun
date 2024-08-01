# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0


from typing import Union

import terrarun.models.organisation
import terrarun.models.user
import terrarun.workspace_execution_mode
import terrarun.models.plan
import terrarun.models.apply

from .base_entity import (
    NestedAttributes,
    Attribute,
    ATTRIBUTED_REQUIRED,
)


class AgentExecutionDetailsEntity(NestedAttributes):
    """Entity for execution details for plan/apply"""

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
    def _from_object(cls, obj: Union['terrarun.models.plan.Plan', 'terrarun.models.apply.Apply'], effective_user: 'terrarun.models.user.User'):
        """Convert plan object agent details entity"""
        attributes = {
            "mode": obj.execution_mode
        }
        if obj.agent is not None:
            attributes["agent_id"] = obj.agent.api_id
            attributes["agent_name"] = obj.agent.name
            attributes["agent_pool_id"] = obj.agent.agent_pool.api_id
            attributes["agent_pool_name"] = obj.agent.agent_pool.name
        return cls(attributes=attributes)
