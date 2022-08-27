# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import sqlalchemy
import sqlalchemy.orm

from terrarun.base_object import BaseObject
from terrarun.database import Base, Database


class Task(Base, BaseObject):

    ID_PREFIX = 'task'

    __tablename__ = 'task'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    url = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.String)
    enabled = sqlalchemy.Column(sqlalchemy.Boolean)
    hmac_key = sqlalchemy.Column(sqlalchemy.String)

    organisation_id = sqlalchemy.Column(sqlalchemy.ForeignKey("organisation.id"), nullable=False)
    organisation = sqlalchemy.orm.relationship("Organisation", back_populates="tasks")

    @classmethod
    def get_by_organisation_and_name(cls, organisation, name):
        """Obtain tag object by organisation and name."""
        session = Database.get_session()
        task = session.query(cls).filter(
            cls.name==name,
            cls.organisation==organisation
        ).first()

        return task

    @classmethod
    def create(cls, organisation, tag_name):
        task = cls(organisation=organisation, name=tag_name)
        session = Database.get_session()
        session.add(task)
        session.commit()
        return task

    def get_api_details(self):
        """Return API details for task"""
        return {
            "id": self.api_id,
            "type": "tasks",
            "attributes": {
                "category": "task",
                "name": self.name,
                "url": self.url,
                "description": self.description,
                "enabled": self.enabled,
                "hmac-key": self.hmac_key,
            },
            "relationships": {
                "organization": {
                    "data": {
                        "id": self.organisation.name,
                        "type": "organizations"
                    }
                },
                "tasks": {
                    "data": []
                }
            },
            "links": {
                "self": f"/api/v2/tasks/{self.api_id}"
            }
        }
