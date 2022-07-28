
import sqlalchemy

from terrarun.base_object import BaseObject
from terrarun.workspace import Workspace
from terrarun.database import Base, Database
from terrarun.config import Config


class Organisation(Base, BaseObject):

    ID_PREFIX = 'org'

    __tablename__ = 'organisation'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)

    workspaces = sqlalchemy.orm.relation("Workspace", back_populates="organisation")

    @classmethod
    def get_by_name(cls, organisation_name):
        """Return organisation object by name of organisation"""
        session = Database.get_session()
        org = session.query(Organisation).filter(Organisation.name==organisation_name).first()

        if not org and Config().AUTO_CREATE_ORGANISATIONS:
            org = Organisation.create(name=organisation_name)
        return org
    
    @classmethod
    def create(cls, name):
        org = cls(name=name)
        session = Database.get_session()
        session.add(org)
        session.commit()
        return org

    def get_entitlement_set_api(self):
        """Return API response for organisation entitlement"""
        return {
            "data": {
                "id": self.api_id,
                "type": "entitlement-sets",
                "attributes": {
                    "cost-estimation": False,
                    "configuration-designer": True,
                    "operations": True,
                    "private-module-registry": False,
                    "sentinel": False,
                    "run-tasks": False,
                    "state-storage": False,
                    "teams": False,
                    "vcs-integrations": False,
                    "usage-reporting": False,
                    "user-limit": 5,
                    "self-serve-billing": True,
                    "audit-logging": False,
                    "agents": False,
                    "sso": False
                },
                "links": {
                    "self": f"/api/v2/entitlement-sets/{self.api_id}"
                }
            }
        }
