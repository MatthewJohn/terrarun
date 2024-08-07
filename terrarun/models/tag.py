# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

import sqlalchemy
import sqlalchemy.orm

from terrarun.models.base_object import BaseObject
from terrarun.database import Base, Database
from terrarun.utils import datetime_to_json
import terrarun.database


class Tag(Base, BaseObject):

    ID_PREFIX = 'tag'

    __tablename__ = 'tag'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    api_id_fk = sqlalchemy.Column(sqlalchemy.ForeignKey("api_id.id"), nullable=True)
    api_id_obj = sqlalchemy.orm.relationship("ApiId", foreign_keys=[api_id_fk])

    name = sqlalchemy.Column(terrarun.database.Database.GeneralString)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=sqlalchemy.sql.func.now())

    organisation_id = sqlalchemy.Column(sqlalchemy.ForeignKey("organisation.id"), nullable=False)
    organisation = sqlalchemy.orm.relationship("Organisation", back_populates="tags")

    workspaces = sqlalchemy.orm.relationship("Workspace", secondary="workspace_tag", back_populates="tags")

    @classmethod
    def get_by_organisation_and_name(cls, organisation, tag_name):
        """Obtain tag object by organisation and name."""
        session = Database.get_session()
        tag = session.query(cls).filter(
            cls.name==tag_name,
            cls.organisation==organisation
        ).first()

        return tag

    @classmethod
    def create(cls, organisation, tag_name):
        tag = cls(organisation=organisation, name=tag_name)
        session = Database.get_session()
        session.add(tag)
        session.commit()
        return tag

    def get_relationship(self):
        """Return relationship data for tag."""
        return {
            "id": self.api_id,
            "type": "tags"
        }

    def get_api_details(self):
        """Return API details for tag"""
        return {
            "id": self.api_id,
            "type": "tags",
            "attributes": {
                "name": self.name,
                "created-at": datetime_to_json(self.created_at),
                "instance-count": 1
            },
            "relationships": {
                "organization": {
                    "data": {
                        "id": self.organisation.name,
                        "type": "organizations"
                    }
                }
            }
        }
