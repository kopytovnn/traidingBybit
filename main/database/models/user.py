from sqlalchemy import MetaData, Table, String, Integer, Column, Text, DateTime, Boolean, ForeignKey, Date
from sqlalchemy.orm import declarative_base, relationship
from database.models.base import Base
# from ...admin_core.app.handlers import add_new_user


class User(Base):
    __tablename__ = 'User'

    id = Column(Integer, nullable=True, unique=True, primary_key=True, autoincrement=True)
    name = Column(String(), nullable=True)
    bybitapi = Column(String(), nullable=True)
    bybitsecret = Column(String(), nullable=True)
    bingxapi = Column(String(), nullable=True)
    bingxsecret = Column(String(), nullable=True)