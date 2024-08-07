# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0


import datetime
from typing import Any, Tuple, Optional

import terrarun.models.organisation
import terrarun.models.user
import terrarun.permissions.organisation
import terrarun.workspace_execution_mode
import terrarun.models.agent_pool
import terrarun.auth_context

from .base_entity import (
    BaseEntity,
    EntityView,
    RelatedRelationshipView,
    RelatedWithDataRelationshipView,
    DataRelationshipView,
    ListEntityView,
    Attribute,
    AttributeModifier,
    ATTRIBUTED_REQUIRED,
    UNDEFINED
)


class OrganizationEntity(BaseEntity):

    type = "organizations"

    @classmethod
    def _get_attributes(cls):
        return (
            Attribute("name", "name", str, ATTRIBUTED_REQUIRED),
            Attribute("email", "email", str, ATTRIBUTED_REQUIRED),
            Attribute("external-id", "external_id", str, None),
            Attribute("created-at", "created_at", datetime.datetime, None),
            Attribute("session-timeout", "session_timeout", int, 20160),
            Attribute("session-remember", "session_remember", int, 20160),
            Attribute("collaborator-auth-policy", "collaborator_auth_policy",
                      terrarun.models.organisation.CollaboratorAuthPolicyType,
                      terrarun.models.organisation.CollaboratorAuthPolicyType.PASSWORD),
            Attribute("plan-expired", "plan_expired", bool, False),
            Attribute("plan-expires-at", "plan_expires_at", str, None),
            Attribute("plan-is-trial", "plan_is_trial", bool, False),
            Attribute("plan-is-enterprise", "plan_is_enterprise", bool, True),
            Attribute("plan-identifier", "plan_identifier", str, "developer"),
            Attribute("cost-estimation-enabled", "cost_estimation_enabled", bool, False),
            Attribute("send-passing-statuses-for-untriggered-speculative-plans", "send_passing_statuses_for_untriggered_speculative_plans", bool, False),
            Attribute("permissions", "permissions", dict, ATTRIBUTED_REQUIRED),
            Attribute("fair-run-queuing-enabled", "fair_run_queuing_enabled", bool, True),
            Attribute("saml-enabled", "saml_enabled", bool, False),
            Attribute("owners-team-saml-role-id", "owners_team_saml_role_id", str, None),
            Attribute("two-factor-conformant", "two_factor_conformant", bool, False),
            Attribute("default-execution-mode", "default_execution_mode",
                      terrarun.workspace_execution_mode.WorkspaceExecutionMode,
                      terrarun.workspace_execution_mode.WorkspaceExecutionMode.REMOTE),
        )

    @classmethod
    def _from_object(cls, obj: 'terrarun.models.organisation.Organisation', auth_context: 'terrarun.auth_context.AuthContext'):
        """Convert object to organisation entity"""
        permission = terrarun.permissions.organisation.OrganisationPermissions(current_user=auth_context.user, organisation=obj)
        return cls(
            id=obj.name_id,
            attributes={
                "external_id": obj.api_id,
                "created_at": obj.created_at,
                "email": obj.email,
                "session_timeout": obj.session_timeout,
                "session_remember": obj.session_remember,
                "collaborator_auth_policy": obj.collaborator_auth_policy,

                # Hard code plan, as this is not implemented
                "plan_expired": False,
                "plan_expires_at": None,
                "plan_is_trial": False,
                "plan_is_enterprise": True,
                "plan_identifier": "developer",

                "cost_estimation_enabled": obj.cost_estimation_enabled,
                "send_passing_statuses_for_untriggered_speculative_plans": obj.send_passing_statuses_for_untriggered_speculative_plans,
                "name": obj.name,
                "permissions": permission.get_api_permissions(),
                "fair_run_queuing_enabled": obj.fair_run_queuing_enabled,
                "saml_enabled": obj.saml_enabled,
                "owners_team_saml_role_id": obj.owners_team_saml_role_id,
                "two_factor_conformant": obj.two_factor_conformant,
                "default_execution_mode": obj.default_execution_mode,
            }
        )


class OrganizationCreateEntity(OrganizationEntity):
    """Entity for organisation creation"""

    require_id = False
    include_attributes = [
        "name",
        "email",
        "session_timeout",
        "session_remember",
        "cost_estimation_enabled",
        "send_passing_statuses_for_untriggered_speculative_plans",
        "owners_team_saml_role_id",
        "default_execution_mode",
    ]


class OrganizationUpdateEntity(OrganizationEntity):
    """Entity for organisation updates"""

    require_id = False
    include_attributes = [
        "name",
        "email",
        "session_timeout",
        "session_remember",
        "cost_estimation_enabled",
        "send_passing_statuses_for_untriggered_speculative_plans",
        "owners_team_saml_role_id",
        "default_execution_mode",
        "default_agent_pool"
    ]
    attribute_modifiers = {
        "name": AttributeModifier(default=UNDEFINED),
        "email": AttributeModifier(default=UNDEFINED),
        "session_timeout": AttributeModifier(default=UNDEFINED),
        "session_remember": AttributeModifier(default=UNDEFINED),
        "cost_estimation_enabled": AttributeModifier(default=UNDEFINED),
        "send_passing_statuses_for_untriggered_speculative_plans": AttributeModifier(default=UNDEFINED),
        "owners_team_saml_role_id": AttributeModifier(default=UNDEFINED),
        "default_execution_mode": AttributeModifier(default=UNDEFINED),
    }

    @classmethod
    def _get_attributes(cls):
        """Override get_attributes to add update-specific arguments"""
        return super()._get_attributes() + (
            Attribute("default-agent-pool-id", "default_agent_pool", terrarun.models.agent_pool.AgentPool, UNDEFINED, True),
        )


class OauthTokensRelationship(RelatedRelationshipView):

    CHILD_PATH = "oauth-tokens"


class OauthClientsRelationship(RelatedRelationshipView):

    CHILD_PATH = "oauth-clients"


class AuthenticationTokenRelationship(RelatedRelationshipView):

    CHILD_PATH = "authentication-token"


class SubscriptionRelationship(RelatedRelationshipView):

    CHILD_PATH = "subscription"


class EntitlementSetRelationship(RelatedWithDataRelationshipView):

    CHILD_PATH = "entitlement-set"
    TYPE       = "entitlement-sets"

    @classmethod
    def get_id_from_object(cls, obj: 'terrarun.models.organisation.Organisation') -> str:
        """Return ID"""
        return obj.api_id


class DefaultAgentPoolRelationship(DataRelationshipView):

    TYPE = "agent-pools"
    OPTIONAL = True

    @classmethod
    def get_id_from_object(cls, obj: 'terrarun.models.organisation.Organisation') -> Optional[str]:
        """Get agent pool ID"""
        if obj.default_agent_pool:
            return obj.default_agent_pool.api_id
        return None


class OrganizationView(OrganizationEntity, EntityView):
    """View for settings"""

    RELATIONSHIPS = {
        "oauth-tokens": OauthTokensRelationship,
        "oauth-clients": OauthClientsRelationship,
        "authentication-token": AuthenticationTokenRelationship,
        "subscription": SubscriptionRelationship,
        "entitlement-set": EntitlementSetRelationship,
        "default-agent-pool": DefaultAgentPoolRelationship,
    }

    @staticmethod
    def generate_link(obj: 'terrarun.models.organisation.Organisation'):
        """Generate self link from given objects"""
        return f'/api/v2/organizations/{obj.name}'


class OrganisationListView(ListEntityView):

    ENTITY_CLASS = OrganizationView
