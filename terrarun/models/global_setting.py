
import sqlalchemy

from terrarun.database import Base, Database


class GlobalSetting(Base):

    __tablename__ = 'global_setting'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    name = sqlalchemy.Column(Database.GeneralString, nullable=False)
    data_type = sqlalchemy.Column(Database.GeneralString, nullable=False)
    value = sqlalchemy.Column(Database.LargeString)

    @classmethod
    def get_setting(cls, name):
        """Get setting by name"""
        session = Database.get_session()
        res = session.query(cls).filter(cls.name==name).first()
        if not res:
            raise Exception("Unknown global setting")

        if res.data_type == "string":
            return res.value
        elif res.data_type == "int":
            return int(res.value)
        elif res.data_type == "bool":
            return bool(res.value)
        else:
            raise Exception("Unknown global setting data type")

    @classmethod
    def update_value(cls, name, value):
        """Update setting with new value"""
        session = Database.get_session()
        res = session.query(cls).filter(cls.name==name).first()
        if not res:
            raise Exception("Unknown global setting")
        
        converted_value = None
        if res.data_type in ["string", "int"]:
            converted_value = str(value)
        elif res.data_type == "bool":
            converted_value = "1" if value else ""
        else:
            raise Exception("Unknown global setting data type")

        res.value = converted_value
        session.add(res)
        session.commit()
