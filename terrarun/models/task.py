# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import re
import sqlalchemy
import sqlalchemy.orm

from terrarun.models.base_object import BaseObject
from terrarun.database import Base, Database
import terrarun.database


class Task(Base, BaseObject):

    ID_PREFIX = 'task'

    __tablename__ = 'task'

    MINIMUM_NAME_LENGTH = 3
    RESERVED_NAMES = []

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    api_id_fk = sqlalchemy.Column(sqlalchemy.ForeignKey("api_id.id"), nullable=True)
    api_id_obj = sqlalchemy.orm.relation("ApiId", foreign_keys=[api_id_fk])

    name = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=False)
    url = sqlalchemy.Column(terrarun.database.Database.GeneralString)
    description = sqlalchemy.Column(terrarun.database.Database.GeneralString)
    enabled = sqlalchemy.Column(sqlalchemy.Boolean)
    hmac_key = sqlalchemy.Column(terrarun.database.Database.GeneralString)

    organisation_id = sqlalchemy.Column(sqlalchemy.ForeignKey("organisation.id"), nullable=False)
    organisation = sqlalchemy.orm.relationship("Organisation", back_populates="tasks")

    workspace_tasks = sqlalchemy.orm.relationship("WorkspaceTask", back_populates="task")

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
    def validate_new_name(cls, organisation, name):
        """Ensure task does not already exist and name isn't reserved"""
        session = Database.get_session()
        existing_workspace = session.query(cls).filter(cls.name==name, cls.organisation==organisation).first()
        if existing_workspace:
            return False
        if name in cls.RESERVED_NAMES:
            return False
        if len(name) < cls.MINIMUM_NAME_LENGTH:
            return False
        if not re.match(r'^[a-zA-Z0-9-_]+$', name):
            return False
        return True

    @classmethod
    def create(cls, organisation, name, description, url, hmac_key, enabled):
        task = cls(organisation=organisation, name=name,
                   description=description, url=url, hmac_key=hmac_key, enabled=enabled)
        session = Database.get_session()
        session.add(task)
        session.commit()
        return task

    def update_attributes(self, **kwargs):
        """Update attributes of task"""

        if 'id' in kwargs or 'organisation' in kwargs:
            # Do not allow update of ID or organisation
            return False

        # If name is specificed in arguments to update,
        # check it is valid
        if ('name' in kwargs and
                kwargs['name'] != self.name and
                not self.validate_new_name(self.organisation, kwargs['name'])):
            return False

        for attr in kwargs:
            setattr(self, attr, kwargs[attr])

        session = Database.get_session()
        session.add(self)
        session.commit()

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
