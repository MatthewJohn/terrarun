# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential


import os
import sqlalchemy
import sqlalchemy.orm

import terrarun.config
import terrarun.database
from terrarun.database import Base, Database
from terrarun.models.base_object import BaseObject
from terrarun.utils import generate_random_secret_string


class AgentToken(Base, BaseObject):

    ID_PREFIX = "at"

    __tablename__ = "agent_token"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    description = sqlalchemy.Column(terrarun.database.Database.GeneralString, default=None)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=sqlalchemy.sql.func.now())
    last_used_at = sqlalchemy.Column(sqlalchemy.DateTime, default=None)

    created_by_id = sqlalchemy.Column(sqlalchemy.ForeignKey("user.id"), nullable=False)
    created_by = sqlalchemy.orm.relationship("User")

    agent_pool_id = sqlalchemy.Column(sqlalchemy.ForeignKey("agent_pool.id"), nullable=False)
    agent_pool = sqlalchemy.orm.relationship("AgentPool")

    token = sqlalchemy.Column(terrarun.database.Database.GeneralString)


    @classmethod
    def get_by_token(cls, token):
        """Obtain agent token object by token value"""
        session = Database.get_session()
        return session.query(cls).filter(cls.token==token).first()

    @classmethod
    def create(cls, agent_pool, created_by):
        """Create agent token"""
        session = Database.get_session()
        agent_token = cls(
            created_by=created_by,
            agent_pool=agent_pool,
            token=generate_random_secret_string()
        )
        session.add(agent_token)
        session.commit()
        return agent_token

    def get_api_details(self):
        """Return details for agent token."""
        return {
            "data": {
                "id": "at-2rG2oYU9JEvfaqji",
                "type": "authentication-tokens",
                "attributes": {
                    "created-at": self.created_at,
                    "last-used-at": self.last_used_at,
                    "description": self.description,
                    "token": self.token
                },
                "relationships": {
                    "created-by": {
                        "data": {
                            "id": self.created_by.api_id,
                            "type": "users"
                        }
                    }
                }
            }
        }

