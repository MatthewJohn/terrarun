# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from enum import Enum
import sqlalchemy
import sqlalchemy.orm

from terrarun.models.base_object import BaseObject
from terrarun.config import Config
import terrarun.models.organisation
import terrarun.models.run
import terrarun.models.configuration
from terrarun.database import Base, Database
import terrarun.database
import terrarun.models.user
import terrarun.utils


class AuditEventType(Enum):
    """Audit event types"""

    STATUS_CHANGE = "status_change"


class AuditEvent(Base, BaseObject):

    ID_PREFIX = 'ae'

    __tablename__ = 'audit_event'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    timestamp = sqlalchemy.Column(sqlalchemy.DateTime, default=sqlalchemy.sql.func.now())

    organisation_id = sqlalchemy.Column(sqlalchemy.ForeignKey("organisation.id"), nullable=False)
    organisation = sqlalchemy.orm.relationship("Organisation", back_populates="audit_events")

    user_id = sqlalchemy.Column(sqlalchemy.Integer)
    object_id = sqlalchemy.Column(sqlalchemy.Integer)
    object_type = sqlalchemy.Column(terrarun.database.Database.GeneralString)

    # Used if a object value has changed
    old_value = sqlalchemy.Column(sqlalchemy.LargeBinary)
    new_value = sqlalchemy.Column(sqlalchemy.LargeBinary)

    event_type = sqlalchemy.Column(sqlalchemy.Enum(AuditEventType))
    event_description = sqlalchemy.Column(terrarun.database.Database.GeneralString)

    comment = sqlalchemy.Column(terrarun.database.Database.GeneralString)

    @classmethod
    def get_by_object_type_and_object_id(cls, object_type, object_id):
        """Return audit events for given object"""
        session = Database.get_session()
        return session.query(cls).where(cls.object_type==object_type, cls.object_id==object_id)

    def get_api_details(self):
        """Return API details for audit event"""
        return {
            "attributes": {
                "old-value": Database.decode_blob(self.old_value),
                "new-value": Database.decode_blob(self.new_value),
                "type": self.event_type.value,
                "description": self.event_description,
                "comment": self.comment,
                "timestamp": terrarun.utils.datetime_to_json(self.timestamp)
            },
            "id": self.api_id,
            "links": {
                "self": f"/api/v2/audit-events/{self.api_id}"
            },
            "relationships": {
                "user": {
                    "data": { "id": self.api_id, "type": "users" } if self.user_id else {}
                }
            },
            "type": "audit-events"
        }
