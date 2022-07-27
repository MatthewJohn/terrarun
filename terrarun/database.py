
import sqlalchemy
import sqlalchemy.orm

Base = sqlalchemy.orm.declarative_base()

class Database:
    """Handle database connection and settng up database schema"""

    _ENGINE = None

    @classmethod
    def get_engine(cls):
        """Get singleton instance of engine."""
        if cls._ENGINE is None:
            cls._ENGINE = sqlalchemy.create_engine('sqlite:///test.db', pool_size=5, pool_recycle=3600)
        return cls._ENGINE
