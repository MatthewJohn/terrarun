
import sqlalchemy
import sqlalchemy.orm

Base = sqlalchemy.orm.declarative_base()

class Database:
    """Handle database connection and settng up database schema"""

    _ENGINE = None
    _SESSION_LOCAL = None

    @classmethod
    def get_engine(cls):
        """Get singleton instance of engine."""
        if cls._ENGINE is None:
            cls._ENGINE = sqlalchemy.create_engine('sqlite:///test.db')
        return cls._ENGINE

    @classmethod
    def get_session(cls):
        """Return database session"""
        return sqlalchemy.orm.Session(cls.get_engine(), future=True, expire_on_commit=False)

    @classmethod
    def get_session_local(cls):
        """Return session local object"""
        if cls._SESSION_LOCAL is None:
            cls._SESSION_LOCAL = sqlalchemy.orm.sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=cls.get_engine()
            )
        return cls._SESSION_LOCAL
