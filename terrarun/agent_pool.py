# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential


import os
import sqlalchemy
import sqlalchemy.orm

import terrarun.config
import terrarun.database
from terrarun.database import Base
from terrarun.base_object import BaseObject


class AgentPool(Base, BaseObject):

    ID_PREFIX = "apool"
    MINIMUM_NAME_LENGTH = 3

    __tablename__ = "agent_pool"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(terrarun.database.Database.GeneralString, default=None)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=sqlalchemy.sql.func.now())

    organisation_id = sqlalchemy.Column(sqlalchemy.ForeignKey("organisation.id"), nullable=True)
    organisation = sqlalchemy.orm.relationship("Organisation")

    agents = sqlalchemy.orm.relation("Agent", back_populates="agent_pool")

    allow_all_workspaces = sqlalchemy.Column(sqlalchemy.Boolean, default=False)


    def get_api_details(self):
        """Return details for agent pool."""
        return {
            "id": self.api_id,
            "type": "agent-pools",
            "attributes": {
                "name": self.name,
                "created-at": self.created_at,
                "organization-scoped": self.organisation is not None
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

