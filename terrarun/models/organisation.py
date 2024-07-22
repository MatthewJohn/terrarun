# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from enum import Enum
from typing import Optional
import re
import sqlalchemy
import sqlalchemy.orm

from terrarun.models.base_object import BaseObject
from terrarun.database import Base, Database
import terrarun.database
from terrarun.config import Config
from terrarun.models.lifecycle import Lifecycle
from terrarun.permissions.organisation import OrganisationPermissions
import terrarun.models.run
import terrarun.models.run_queue
import terrarun.models.configuration
from terrarun.models.team import Team
from terrarun.utils import datetime_to_json
import terrarun.models.workspace
import terrarun.api_entities.organization
import terrarun.workspace_execution_mode


class CollaboratorAuthPolicyType(Enum):

    PASSWORD = 'password'
    TWO_FACTORY_MANDATORY = 'two_factor_mandatory'


class Organisation(Base, BaseObject):

    ID_PREFIX = 'org'
    RESERVED_ORGANISATION_NAMES = ["organisation"]
    MINIMUM_NAME_LENGTH = 3

    __tablename__ = 'organisation'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    api_id_fk = sqlalchemy.Column(sqlalchemy.ForeignKey("api_id.id"), nullable=True)
    api_id_obj = sqlalchemy.orm.relation("ApiId", foreign_keys=[api_id_fk])

    # User-chosen name of org
    name = sqlalchemy.Column(terrarun.database.Database.GeneralString)
    # Name used for URLs and API references
    name_id = sqlalchemy.Column(terrarun.database.Database.GeneralString, unique=True)
    # Admin email address
    email = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=True)

    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=sqlalchemy.sql.func.now())

    # User session invactivity timeout
    session_timeout = sqlalchemy.Column(sqlalchemy.Integer, default=20160)
    # User session timeout when 'remeber-me' is enabled
    session_remember = sqlalchemy.Column(sqlalchemy.Integer, default=20160)

    collaborator_auth_policy = sqlalchemy.Column(
        sqlalchemy.Enum(CollaboratorAuthPolicyType),
        default=CollaboratorAuthPolicyType.PASSWORD
    )

    # Feature flags for organisation - default unimplemented features to False
    cost_estimation_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    configuration_designer_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    operations_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    private_registry_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    sentinel_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    run_tasks_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    state_storage_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    team_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    vcs_integration_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    usage_reporting_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    self_serve_billing_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    audit_logging_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    agents_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    sso_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    default_execution_mode = sqlalchemy.Column(
        sqlalchemy.Enum(terrarun.workspace_execution_mode.WorkspaceExecutionMode),
        default=terrarun.workspace_execution_mode.WorkspaceExecutionMode.AGENT,
        nullable=False
    )

    fair_run_queuing_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    two_factor_conformant = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    saml_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    # Default user limit to None (unlimited)
    user_limit = sqlalchemy.Column(sqlalchemy.Integer, default=None)

    send_passing_statuses_for_untriggered_speculative_plans = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    owners_team_saml_role_id = sqlalchemy.Column(terrarun.database.Database.GeneralString, default=None)

    workspaces = sqlalchemy.orm.relation("Workspace", back_populates="organisation")
    tags = sqlalchemy.orm.relation("Tag", back_populates="organisation")
    audit_events = sqlalchemy.orm.relation("AuditEvent", back_populates="organisation")
    environments = sqlalchemy.orm.relation("Environment", back_populates="organisation")
    lifecycles = sqlalchemy.orm.relation("Lifecycle", back_populates="organisation", foreign_keys=[Lifecycle.organisation_id])
    projects = sqlalchemy.orm.relation("Project", back_populates="organisation")
    oauth_clients = sqlalchemy.orm.relation("OauthClient", back_populates="organisation")

    default_lifecycle_id = sqlalchemy.Column(
        sqlalchemy.ForeignKey("lifecycle.id", name="fk_organisation_default_lifecycle_id_lifecycle_id"),
        default=None, nullable=True
    )
    default_lifecycle = sqlalchemy.orm.relationship("Lifecycle", foreign_keys=[default_lifecycle_id], lazy=True)

    teams = sqlalchemy.orm.relation("Team", back_populates="organisation")

    tasks = sqlalchemy.orm.relation("Task", back_populates="organisation")

    @classmethod
    def get_by_name_id(cls, name_id: str) -> Optional['Organisation']:
        """Return organisation object by name of organisation"""
        session = Database.get_session()
        org = session.query(Organisation).filter(Organisation.name_id==name_id).first()
        return org
    
    @staticmethod
    def name_to_name_id(name: str) -> str:
        """Convert organisation to a name ID"""
        return re.sub(r'[^0-9^a-z^A-Z]+', '-', name).replace('--', '-').lower()

    @classmethod
    def validate_new_name_id(cls, name_id: str) -> bool:
        """Ensure organisation does not already exist and name isn't reserved"""
        session = Database.get_session()
        existing_org = session.query(cls).filter(cls.name_id == name_id).first()
        if existing_org:
            return False
        if name_id in cls.RESERVED_ORGANISATION_NAMES:
            return False
        if len(name_id) < cls.MINIMUM_NAME_LENGTH:
            return False
        return True

    @classmethod
    def create(cls, name: str, email: str) -> 'Organisation':
        """Create organisation"""
        name_id = cls.name_to_name_id(name)

        if not cls.validate_new_name_id(name_id):
            return None

        org = cls(name=name, name_id=name_id, email=email)
        session = Database.get_session()
        session.add(org)
        session.commit()

        # @TODO Create owners group

        return org

    def update_attributes(self, **kwargs):
        """Update attributes of organisation"""
        # If name_id has been specified, remove it, as this
        # cannot be set manually.
        if 'name_id' in kwargs:
            del(kwargs['name_id'])

        # If name is specificed in arguments to update,
        # update the name_id
        if 'name' in kwargs:
            new_name_id = self.name_to_name_id(kwargs['name'])

            # If the name ID differs from the current one,
            # validate it
            if new_name_id != self.name_id:
                if not self.validate_new_name_id(name_id=new_name_id):
                    return False
            kwargs['name_id'] = new_name_id

        for attr in kwargs:
            setattr(self, attr, kwargs[attr])

        session = Database.get_session()
        session.add(self)
        session.commit()
        return True


    def update_from_entity(self, update_entity: 'terrarun.api_entities.organization.OrganizationUpdateEntity'):
        """Update organisation from entity"""

        for attribute, value in update_entity.get_set_object_attributes().items():
            if attribute == "name":
                new_name_id = self.name_to_name_id(value)

                # If the name ID differs from the current one,
                # validate it
                if new_name_id != self.name_id:
                    if not self.validate_new_name_id(name_id=new_name_id):
                        return False
                    self.name_id = new_name_id

            setattr(self, attribute, value)

        session = Database.get_session()
        session.add(self)
        session.commit()
        return True

    def get_run_queue(self):
        """Return runs queued to be executed"""
        session = Database.get_session()
        run_queues = session.query(
            terrarun.models.run_queue.RunQueue
        ).join(
            terrarun.models.run.Run
        ).join(
            terrarun.models.configuration.ConfigurationVersion
        ).join(
            terrarun.models.workspace.Workspace
        ).filter(
            terrarun.models.workspace.Workspace.organisation == self
        )
        return [
            run_queue.run for run_queue in run_queues
        ]

    def get_entitlement_set_api(self):
        """Return API response for organisation entitlement"""
        return {
            "data": {
                "id": self.api_id,
                "type": "entitlement-sets",
                "attributes": {
                    "cloud": True,
                    "cost-estimation": self.cost_estimation_enabled,
                    "configuration-designer": self.configuration_designer_enabled,
                    "operations": self.operations_enabled,
                    "private-module-registry": self.private_registry_enabled,
                    "sentinel": self.sentinel_enabled,
                    "run-tasks": self.run_tasks_enabled,
                    "state-storage": self.state_storage_enabled,
                    "teams": self.team_enabled,
                    "vcs-integrations": self.vcs_integration_enabled,
                    "usage-reporting": self.usage_reporting_enabled,
                    "user-limit": self.user_limit,
                    "self-serve-billing": self.self_serve_billing_enabled,
                    "audit-logging": self.audit_logging_enabled,
                    "agents": self.agents_enabled,
                    "sso": self.sso_enabled
                },
                "links": {
                    "self": f"/api/v2/entitlement-sets/{self.api_id}"
                }
            }
        }

    def get_api_details(self, effective_user):
        """Return API details for organisation"""
        permission = OrganisationPermissions(current_user=effective_user, organisation=self)
        return {
            "id": self.name_id,
            "type": "organizations",
            "attributes": {
                "external-id": self.api_id,
                "created-at": datetime_to_json(self.created_at),
                "email": self.email,
                "session-timeout": self.session_timeout,
                "session-remember": self.session_remember,
                "collaborator-auth-policy": self.collaborator_auth_policy.value,

                # Hard code plan, as this is not implemented
                "plan-expired": False,
                "plan-expires-at": None,
                "plan-is-trial": False,
                "plan-is-enterprise": True,
                "plan-identifier": "developer",

                "cost-estimation-enabled": self.cost_estimation_enabled,
                "send-passing-statuses-for-untriggered-speculative-plans": self.send_passing_statuses_for_untriggered_speculative_plans,
                "name": self.name,
                "permissions": permission.get_api_permissions(),
                "fair-run-queuing-enabled": self.fair_run_queuing_enabled,
                "saml-enabled": self.saml_enabled,
                "owners-team-saml-role-id": self.owners_team_saml_role_id,
                "two-factor-conformant": self.two_factor_conformant
            },
            "relationships": {
                "oauth-tokens": {
                    "links": {
                        "related": f"/api/v2/organizations/{self.name}/oauth-tokens"
                    }
                },
                "oauth-clients": {
                    "links": {
                        "related": f"/api/v2/organizations/{self.name}/oauth-clients"
                    }
                },
                "authentication-token": {
                    "links": {
                        "related": f"/api/v2/organizations/{self.name}/authentication-token"
                    }
                },
                "entitlement-set": {
                    "data": {
                        "id": self.api_id,
                        "type": "entitlement-sets"
                    },
                    "links": {
                        "related": f"/api/v2/organizations/{self.name}/entitlement-set"
                    }
                },
                "subscription": {
                    "links": {
                        "related": f"/api/v2/organizations/{self.name}/subscription"
                    }
                }
            },
            "links": {
                "self": f"/api/v2/organizations/{self.name}"
            }
        }
