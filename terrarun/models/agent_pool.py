# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

import os
import sqlalchemy
import sqlalchemy.orm

import terrarun.config
import terrarun.database
from terrarun.database import Base, Database
from terrarun.models.base_object import BaseObject
import terrarun.utils


class AgentPool(Base, BaseObject):

    ID_PREFIX = "apool"
    MINIMUM_NAME_LENGTH = 3

    __tablename__ = "agent_pool"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(terrarun.database.Database.GeneralString, default=None)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=sqlalchemy.sql.func.now())

    api_id_fk = sqlalchemy.Column(sqlalchemy.ForeignKey("api_id.id"), nullable=True)
    api_id_obj = sqlalchemy.orm.relation("ApiId", foreign_keys=[api_id_fk])

    organisation_id = sqlalchemy.Column(sqlalchemy.ForeignKey("organisation.id", name="fk_agent_pool_organisation_id"), nullable=True)
    organisation = sqlalchemy.orm.relationship("Organisation", foreign_keys=[organisation_id])

    agents = sqlalchemy.orm.relation("Agent", back_populates="agent_pool")

    allow_all_workspaces = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    @classmethod
    def create(cls, name, organisation, allow_all_workspaces):
        """Create agent pool"""
        session = Database.get_session()
        agent_pool = cls(
            name=name,
            organisation=organisation,
            allow_all_workspaces=allow_all_workspaces
        )
        session.add(agent_pool)
        session.commit()
        return agent_pool

    @classmethod
    def get_by_organisation(cls, organisation, include_global):
        """Obtain all agent pools"""
        session = Database.get_session()
        query = session.query(cls)
        if include_global:
            query = query.filter(sqlalchemy.or_(cls.organisation==organisation, cls.organisation_id==None))
        else:
            query = query.filter(cls.organisation==organisation)
        return query.all()

    @classmethod
    def get_by_name_and_organisation(cls, name, organisation):
        """Obtain agent pool by organisation and name"""
        session = Database.get_session()
        return session.query(cls).filter(cls.name==name, cls.organisation==organisation).first()

    def get_api_details(self):
        """Return details for agent pool."""
        return {
            "id": self.api_id,
            "type": "agent-pools",
            "attributes": {
                "name": self.name,
                "created-at": terrarun.utils.datetime_to_json(self.created_at),
                "organization-scoped": self.organisation is not None,
                "agent-count": len(self.agents)
            },
            "relationships": {
                "agents": {
                    "links": {
                        "related": f"/api/v2/agent-pools/{self.api_id}/agents"
                    }
                },
                "authentication-tokens": {
                    "links": {
                        "related": f"/api/v2/agent-pools/{self.api_id}/authentication-tokens"
                    }
                },
                "workspaces": {
                    "data": [
                        {
                            "id": "ws-9EEkcEQSA3XgWyGe",
                            "type": "workspaces"
                        }
                    ]
                },
                "allowed-workspaces": {
                    "data": [
                        {
                            "id": "ws-x9taqV23mxrGcDrn",
                            "type": "workspaces"
                        }
                    ]
                }
            },
            "links": {
                "self": f"/api/v2/agent-pools/{self.api_id}"
            }
        }

