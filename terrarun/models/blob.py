# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import sqlalchemy

from terrarun.models.base_object import BaseObject
from terrarun.database import Base



class Blob(Base, BaseObject):
    """Interface for uploaded configuration files"""

    ID_PREFIX = 'blob'

    __tablename__ = 'blob'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    api_id_fk = sqlalchemy.Column(sqlalchemy.ForeignKey("api_id.id"), nullable=True)
    api_id_obj = sqlalchemy.orm.relation("ApiId", foreign_keys=[api_id_fk])

    # Create blob of 200MB
    data = sqlalchemy.Column(sqlalchemy.LargeBinary(length=((2**20) * 200)))
