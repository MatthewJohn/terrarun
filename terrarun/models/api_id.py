
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
    object_class = sqlalchemy.Column(terrarun.database.Database.GeneralString)
    object_id = sqlalchemy.Column(sqlalchemy.Integer)

    __table_args__ = (
        sqlalchemy.UniqueConstraint('object_class', 'object_id', name='_object_class_object_id_uc'),
        sqlalchemy.Index('_object_class_object_id_in', 'object_class', 'object_id'),
        sqlalchemy.Index('_api_id_suffix_index', 'api_id_suffix'),
    )

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
        res = session.query(cls).filter(
            cls.object_class==target_class.__name__,
            cls.api_id_suffix==stripped_id
        ).first()
        if not res:
            return None

        return res.object_id

    @classmethod
    def get_api_id(cls, obj):
        """Return api ID for given object"""
        if not 'id' in dir(obj) or not obj.id:
            raise Exception("Object does not have an ID")

        if not 'ID_PREFIX' in dir(obj) or not obj.ID_PREFIX:
            raise Exception("Object does not have an ID prefix")

        session = Database.get_session()

        object_class = obj.__class__.__name__
        object_id = obj.id

        api_id_object = session.query(cls).filter(
            cls.object_class==object_class,
            cls.object_id==object_id
        ).first()

        if not api_id_object:
            api_id_object = cls(
                object_class=object_class,
                object_id=object_id,
                api_id_suffix=cls._generate_api_id()
            )
            session.add(api_id_object)
            session.commit()

        return f"{obj.ID_PREFIX}-{api_id_object.api_id_suffix}"


