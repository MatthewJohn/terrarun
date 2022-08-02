
from enum import Enum
import re
import sqlalchemy
import sqlalchemy.orm

from terrarun.base_object import BaseObject
from terrarun.database import Base, Database
from terrarun.config import Config
from terrarun.permissions.organisation import OrganisationPermissions
import terrarun.run
import terrarun.run_queue
import terrarun.configuration
from terrarun.team import Team
from terrarun.utils import datetime_to_json
import terrarun.workspace


class CollaboratorAuthPolicyType(Enum):

    PASSWORD = 'password'
    TWO_FACTORY_MANDATORY = 'two_factor_mandatory'


class Organisation(Base, BaseObject):

    ID_PREFIX = 'org'
    RESERVED_ORGANISATION_NAMES = ["organisation"]
    MINIMUM_NAME_LENGTH = 3

    __tablename__ = 'organisation'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    # User-chosen name of org
    name = sqlalchemy.Column(sqlalchemy.String)
    # Name used for URLs and API references
    name_id = sqlalchemy.Column(sqlalchemy.String, unique=True)
    # Admin email address
    email = sqlalchemy.Column(sqlalchemy.String, nullable=True)

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
    run_tasks_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    state_storage_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    team_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    vcs_integration_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    usage_reporting_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    self_serve_billing_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    audit_logging_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    agents_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    sso_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    fair_run_queuing_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    two_factor_conformant = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    saml_enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    # Default user limit to None (unlimited)
    user_limit = sqlalchemy.Column(sqlalchemy.Integer, default=None)

    send_passing_statuses_for_untriggered_speculative_plans = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    owners_team_saml_role_id = sqlalchemy.Column(sqlalchemy.String, default=None)

    workspaces = sqlalchemy.orm.relation("Workspace", back_populates="organisation")

    teams = sqlalchemy.orm.relation("Team", back_populates="organisation")

    @classmethod
    def get_by_name_id(cls, name_id):
        """Return organisation object by name of organisation"""
        session = Database.get_session()
        org = session.query(Organisation).filter(Organisation.name_id==name_id).first()
        return org
    
    @staticmethod
    def name_to_name_id(name):
        """Convert organisation to a name ID"""
        return re.sub(r'[^0-9^a-z^A-Z]+', '-', name).replace('--', '-').lower()

    @classmethod
    def validate_new_name_id(cls, name_id):
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
    def create(cls, name, email):
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

    def get_run_queue(self):
        """Return runs queued to be executed"""
        session = Database.get_session()
        run_queues = session.query(
            terrarun.run_queue.RunQueue
        ).join(
            terrarun.run.Run
        ).join(
            terrarun.configuration.ConfigurationVersion
        ).join(
            terrarun.workspace.Workspace
        ).filter(
            terrarun.workspace.Workspace.organisation == self
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