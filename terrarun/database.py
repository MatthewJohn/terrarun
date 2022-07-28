
import sqlalchemy
import sqlalchemy.orm


class Database:
    """Handle database connection and settng up database schema"""

    _ENGINE = None
    _SESSION_MAKER = None

    @classmethod
    def get_engine(cls):
        """Get singleton instance of engine."""
        if cls._ENGINE is None:
            cls._ENGINE = sqlalchemy.create_engine('sqlite:///test.db')
        return cls._ENGINE

    @classmethod
    def get_session(cls):
        """Return database session"""
        return sqlalchemy.orm.scoped_session(cls.get_session_maker())

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

Base = sqlalchemy.orm.declarative_base()
Base.query = Database.get_session().query_property()
