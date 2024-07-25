# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0


import datetime

import terrarun.models.organisation
import terrarun.models.user
import terrarun.workspace_execution_mode
import terrarun.models.agent_pool

from .base_entity import (
    BaseEntity,
    EntityView,
    RelatedRelationshipView,
    Attribute,
    ATTRIBUTED_REQUIRED,
)


class AgentPoolEntity(BaseEntity):

    type = "agent-pools"

    @classmethod
    def _get_attributes(cls):
        return (
            Attribute("name", "name", str, ATTRIBUTED_REQUIRED),
            Attribute("created-at", "created_at", datetime.datetime, None),
            Attribute("organization-scoped", "organisation_scoped", bool, True),
            Attribute("agent-count", "agent_count", int, ATTRIBUTED_REQUIRED),
        )

    @classmethod
    def _from_object(cls, obj: 'terrarun.models.agent_pool.AgentPool', effective_user: 'terrarun.models.user.User'):
        """Convert object to saml settings entity"""
        return cls(
            id=obj.api_id,
            attributes={
                "name": obj.name,
                "created_at": obj.created_at,
                "organisation_scoped": obj.organisation_scoped,
                "agent_count": len(obj.agents),
            }
        )


class AgentsRelationship(RelatedRelationshipView):

    CHILD_PATH = "agents"


class AuthenticationTokensRelationship(RelatedRelationshipView):

    CHILD_PATH = "authentication-tokens"


class AgentPoolView(AgentPoolEntity, EntityView):
    """View for settings"""

    RELATIONSHIPS = {
        "agents": AgentsRelationship,
        "authentication-tokens": AuthenticationTokensRelationship,
    }

    @staticmethod
    def generate_link(obj: 'terrarun.models.agent_pool.AgentPool') -> str:
        """Generate self link from given objects"""
        return f'/api/v2/agent-pools/{obj.api_id}'
