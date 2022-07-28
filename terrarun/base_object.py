
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
        for itx, char in enumerate(stripped_id):
            if itx == cls.ID_LENGTH:
                raise Exception('ID too long')

            id += (cls.ID_BASE_62.index(char) * pow(62, itx))
        return id

    @property
    def api_id(self):
        """Generate API ID for object"""
        if self.ID_PREFIX is None:
            raise Exception('Object must override ID_PREFIX')

        id = self.id
        api_id = ''
        while id != 0:
            api_id = self.ID_BASE_62[id % self.ID_BASE] + api_id    
            id //= self.ID_BASE
        return api_id.zfill(self.ID_LENGTH)

    @classmethod
    def get_by_api_id(cls, id):
        """Return object by API ID"""
        id = cls.db_id_from_api_id(id)
        session = Database.get_session()
        return session.query(cls).where(cls.id==id).first()
