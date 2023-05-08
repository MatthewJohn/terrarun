# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from math import pow

from terrarun.database import Database
from terrarun.models.api_id import ApiId


class BaseObject:

    ID_PREFIX = None
    ID_BASE_62 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    ID_BASE = len(ID_BASE_62)
    ID_LENGTH = 16

    @classmethod
    def db_id_from_api_id(cls, api_id):
        """Obtain database ID from given API ID"""
        return ApiId.get_db_id_from_api_id(target_class=cls, api_id=api_id)

    @property
    def api_id(self):
        """Generate API ID for object"""
        return ApiId.get_api_id(self)

    @classmethod
    def get_by_api_id(cls, id):
        """Return object by API ID"""

        id = cls.db_id_from_api_id(id)
        if id is None:
            return None

        return cls.get_by_id(id)

    @classmethod
    def get_by_id(cls, id):
        """Return object by ID"""
        session = Database.get_session()
        return session.query(cls).where(cls.id==id).first()

    def __eq__(self, comp):
        """Check if current object is equal to another, comparing API ID"""
        if isinstance(comp, BaseObject):
            return self.api_id == comp.api_id
        return super(BaseObject, self).__eq__(comp)

    def update_attributes(self, session=None, **kwargs):
        """Update attributes of task result"""

        for attr in kwargs:
            setattr(self, attr, kwargs[attr])

        if session is None:
            session = Database.get_session()
            should_commit = True
        else:
            should_commit = False
        session.add(self)
        if should_commit:
            session.commit()
