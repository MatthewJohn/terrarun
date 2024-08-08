# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

from typing_extensions import Self

from math import pow

import terrarun.database
from terrarun.models.api_id import ApiId
import terrarun.logger


logger = terrarun.logger.get_logger(__name__)


class BaseObject:

    ID_PREFIX = None
    ID_BASE_62 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    ID_BASE = len(ID_BASE_62)
    ID_LENGTH = 16

    @classmethod
    def db_id_from_api_id(cls, api_id: str) -> int:
        """Obtain database ID from given API ID"""
        return ApiId.get_db_id_from_api_id(target_class=cls, api_id=api_id)

    @property
    def api_id(self) -> str:
        """Generate API ID for object"""
        return ApiId.get_api_id(self)

    @classmethod
    def get_by_api_id(cls, id: str) -> Self:
        """Return object by API ID"""

        id = cls.db_id_from_api_id(id)
        if id is None:
            return None

        return cls.get_by_id(id)

    @classmethod
    def get_by_id(cls, id: int) -> Self:
        """Return object by ID"""
        session = terrarun.database.Database.get_session()
        return session.query(cls).where(cls.id==id).first()

    def __eq__(self, comp) -> bool:
        """Check if current object is equal to another, comparing API ID"""
        if isinstance(comp, BaseObject):
            return self.api_id == comp.api_id
        return super(BaseObject, self).__eq__(comp)

    def update_attributes(self, session=None, **kwargs):
        """Update attributes of task result"""

        for attr in kwargs:
            setattr(self, attr, kwargs[attr])

        if session is None:
            session = terrarun.database.Database.get_session()
            should_commit = True
        else:
            should_commit = False
        session.add(self)
        if should_commit:
            session.commit()


def update_object_status(obj, new_status, current_user=None, session=None):
    """Update state of run."""
    logger.debug("Updating %s to from %s to %s", obj, obj.status, new_status)
    should_commit = False
    if session is None:
        session = terrarun.database.Database.get_session()
        session.refresh(obj)
        should_commit = True

    audit_event = terrarun.models.audit_event.AuditEvent(
        organisation=obj.organisation,
        user_id=current_user.id if current_user else None,
        object_id=obj.id,
        object_type=obj.ID_PREFIX,
        old_value=terrarun.database.Database.encode_value(obj.status.value) if obj.status else None,
        new_value=terrarun.database.Database.encode_value(new_status.value),
        event_type=terrarun.models.audit_event.AuditEventType.STATUS_CHANGE)

    obj.update_attributes(status=new_status, session=session)

    session.add(obj)
    session.add(audit_event)
    if should_commit:
        session.commit()

