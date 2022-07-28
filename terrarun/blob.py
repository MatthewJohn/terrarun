
import sqlalchemy

from terrarun.base_object import BaseObject
from terrarun.database import Base



class Blob(Base, BaseObject):
    """Interface for uploaded configuration files"""

    ID_PREFIX = 'blob'

    __tablename__ = 'blob'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    data = sqlalchemy.Column(sqlalchemy.LargeBinary)
