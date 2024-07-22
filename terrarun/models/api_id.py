# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0


import secrets
import string
import sqlalchemy

from terrarun.database import Base, Database
import terrarun.database


class ApiId(Base):
    """DB model for associating a random API ID to an object"""

    __tablename__ = "api_id"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    api_id_suffix = sqlalchemy.Column(terrarun.database.Database.GeneralString, unique=True)

    @classmethod
    def _generate_api_id(cls):
        """Generate random ID for object"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for i in range(16))

    @classmethod
    def get_db_id_from_api_id(cls, target_class, api_id):
        """Get DB ID from api id"""
        if len(api_id.split('-')) != 2:
            return None

        stripped_id = api_id.split('-')[1]
        if len(stripped_id) != 16:
            return None

        session = Database.get_session()
        res = session.query(target_class).join(cls).filter(
            cls.api_id_suffix==stripped_id
        ).first()
        if not res:
            return None

        return res.id

    @classmethod
    def get_api_id(cls, obj):
        """Return api ID for given object"""
        if not 'ID_PREFIX' in dir(obj) or not obj.ID_PREFIX:
            raise Exception("Object does not have an ID prefix")

        session = Database.get_session()

        if obj.api_id_obj is None:
            api_id_object = cls(
                api_id_suffix=cls._generate_api_id()
            )
            session.add(api_id_object)
            obj.api_id_obj = api_id_object
            session.add(api_id_object)
            session.commit()

        return f"{obj.ID_PREFIX}-{obj.api_id_obj.api_id_suffix}"


