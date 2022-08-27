# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from math import pow

from terrarun.database import Database


class BaseObject:

    ID_PREFIX = None
    ID_BASE_62 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    ID_BASE = len(ID_BASE_62)
    ID_LENGTH = 16

    @classmethod
    def db_id_from_api_id(cls, api_id):
        if len(api_id.split('-')) != 2:
            return None

        stripped_id = api_id.split('-')[1]
        if len(stripped_id) != 16:
            return None

        id = 0

        # Iterate over ID, in reverse order, so that first digit is the first value
        for itx, char in enumerate(stripped_id[::-1]):
            if itx == cls.ID_LENGTH:
                raise Exception('ID too long')

            id += (cls.ID_BASE_62.index(char) * pow(62, itx))
        return int(id)

    @property
    def api_id(self):
        """Generate API ID for object"""
        return self.api_id_from_db_id(self.id)
    
    @classmethod
    def api_id_from_db_id(cls, id):
        """Convert DB ID to API ID"""
        if cls.ID_PREFIX is None:
            raise Exception('Object must override ID_PREFIX')

        api_id = ''
        while id != 0:
            api_id = cls.ID_BASE_62[id % cls.ID_BASE] + api_id    
            id //= cls.ID_BASE
        api_id = api_id.zfill(cls.ID_LENGTH)
        return f'{cls.ID_PREFIX}-{api_id}'

    @classmethod
    def get_by_api_id(cls, id):
        """Return object by API ID"""

        id = cls.db_id_from_api_id(id)
        if id is None:
            return None

        session = Database.get_session()
        return session.query(cls).where(cls.id==id).first()
