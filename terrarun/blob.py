# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import sqlalchemy

from terrarun.base_object import BaseObject
from terrarun.database import Base



class Blob(Base, BaseObject):
    """Interface for uploaded configuration files"""

    ID_PREFIX = 'blob'

    __tablename__ = 'blob'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    data = sqlalchemy.Column(sqlalchemy.LargeBinary)
