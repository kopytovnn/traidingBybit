from sqlalchemy import MetaData, Table, String, Integer, Column, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from models.base import Base


class ByBitUser(Base):
    __tablename__ = 'ByBitUser'

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    telegram_id = Column(String(), nullable=False)

    apikey = Column(String, nullable=True)
    secretkey = Column(String, nullable=True)