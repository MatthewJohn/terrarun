# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from enum import Enum
import sqlalchemy
import sqlalchemy.orm

from terrarun.base_object import BaseObject
from terrarun.config import Config
import terrarun.organisation
import terrarun.run
import terrarun.configuration
from terrarun.database import Base, Database
import terrarun.user


class AuditEvent(Base, BaseObject):

    ID_PREFIX = 'ae'

    __tablename__ = 'audit_event'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    timestamp = sqlalchemy.Column(sqlalchemy.DateTime, default=sqlalchemy.sql.func.now())

    organisation_id = sqlalchemy.Column(sqlalchemy.ForeignKey("organisation.id"), nullable=False)
    organisation = sqlalchemy.orm.relationship("Organisation", back_populates="audit_events")

    user_id = sqlalchemy.Column(sqlalchemy.Integer)
    object_id = sqlalchemy.Column(sqlalchemy.Integer)
    object_type = sqlalchemy.Column(sqlalchemy.String)

    # Used if a object value has changed
    old_value = sqlalchemy.Column(sqlalchemy.LargeBinary)
    new_value = sqlalchemy.Column(sqlalchemy.LargeBinary)

    event_type = sqlalchemy.Column(sqlalchemy.String)
    event_description = sqlalchemy.Column(sqlalchemy.String)

    comment = sqlalchemy.Column(sqlalchemy.String)


    def get_api_details(self):
        """Return API details for audit event"""
        return {
            "attributes": {
                "old-value": self.old_value,
                "new-value": self.new_value,
                "type": self.event_type,
                "description": self.event_description,
                "comment": self.comment
            },
            "id": self.api_id,
            "links": {
                "self": f"/api/v2/audit-events/{self.api_id}"
            },
            "relationships": {
                "authentication-token": {
                    "meta": {}
                },
                "user": {
                    "data": { "id": terrarun.user.User.api_id_from_db_id(self.user_id), "type": "users" }
                }
            },
            "type": "audit-events"
        }
