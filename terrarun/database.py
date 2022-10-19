# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

try:
    from greenlet import getcurrent as _ident_func
except ImportError:
    from threading import get_ident as _ident_func

# from threading import get_ident as _ident_func
import sqlalchemy
import sqlalchemy.orm

from terrarun.config import Config


class Database:
    """Handle database connection and settng up database schema"""

    _ENGINE = None
    _SESSION_MAKER = None
    _SESSIONS = {}
    blob_encoding_format = 'utf-8'

    @classmethod
    def get_engine(cls):
        """Get singleton instance of engine."""
        if cls._ENGINE is None:
            cls._ENGINE = sqlalchemy.create_engine(Config().DATABASE_URL)
        return cls._ENGINE

    @classmethod
    def get_session(cls):
        """Return database session"""
        thread_id = _ident_func()
        if thread_id not in cls._SESSIONS:
            cls._SESSIONS[thread_id] = sqlalchemy.orm.scoped_session(
                cls.get_session_maker()
            )
        return cls._SESSIONS[thread_id]

    @classmethod
    def get_session_maker(cls):
        """Return session local object"""
        if cls._SESSION_MAKER is None:
            cls._SESSION_MAKER = sqlalchemy.orm.sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=cls.get_engine()
            )
        return cls._SESSION_MAKER

    @classmethod
    def encode_value(cls, value):
        """Encode value for binary blob"""
        if not value:
            value = ''
        return value.encode(cls.blob_encoding_format)

    @classmethod
    def decode_blob(cls, value):
        """Decode blob as a string."""
        if value is None:
            return None
        return value.decode(cls.blob_encoding_format)


Base = sqlalchemy.orm.declarative_base()
Base.query = Database.get_session().query_property()
