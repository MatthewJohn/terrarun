
import datetime
from typing import Tuple

import terrarun.models.organisation
import terrarun.models.user
import terrarun.permissions.organisation
import terrarun.workspace_execution_mode

from .base_entity import BaseEntity, EntityView, Attribute, ATTRIBUTED_REQUIRED, UNDEFINED


class BaseOrganizationEntity(BaseEntity):

    type = "organizations"


class OrganizationUpdateEntity(BaseOrganizationEntity):

    require_id = False

    @classmethod
    def get_attributes(cls) -> Tuple[Attribute]:
        return (
            Attribute("name", "name", str, UNDEFINED),
            Attribute("email", "email", str, UNDEFINED),
            Attribute("default-execution-mode", "default_execution_mode",
                      terrarun.workspace_execution_mode.WorkspaceExecutionMode,
                      terrarun.workspace_execution_mode.WorkspaceExecutionMode.REMOTE),
        )


class OrganizationEntity(BaseOrganizationEntity):

    @classmethod
    def get_attributes(cls):
        return OrganizationUpdateEntity.get_attributes() + (
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
        )

    @classmethod
    def from_object(cls, obj: 'terrarun.models.organisation.Organisation', effective_user: 'terrarun.models.user.User'):
        """Convert object to saml settings entity"""
        permission = terrarun.permissions.organisation.OrganisationPermissions(current_user=effective_user, organisation=obj)
        return cls(
            id=obj.name_id,
            external_id=obj.api_id,
            created_at=obj.created_at,
            email=obj.email,
            session_timeout=obj.session_timeout,
            session_remember=obj.session_remember,
            collaborator_auth_policy=obj.collaborator_auth_policy,

            # Hard code plan, as this is not implemented
            plan_expired=False,
            plan_expires_at=None,
            plan_is_trial=False,
            plan_is_enterprise=True,
            plan_identifier="developer",

            cost_estimation_enabled=obj.cost_estimation_enabled,
            send_passing_statuses_for_untriggered_speculative_plans=obj.send_passing_statuses_for_untriggered_speculative_plans,
            name=obj.name,
            permissions=permission.get_api_permissions(),
            fair_run_queuing_enabled=obj.fair_run_queuing_enabled,
            saml_enabled=obj.saml_enabled,
            owners_team_saml_role_id=obj.owners_team_saml_role_id,
            two_factor_conformant=obj.two_factor_conformant,
            default_execution_mode=obj.default_execution_mode,
        )


class OrganizationView(OrganizationEntity, EntityView):
    """View for settings"""
    pass
