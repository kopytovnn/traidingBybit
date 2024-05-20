from sqlalchemy import MetaData, Table, String, Integer, Column, Text, DateTime, Boolean, ForeignKey, Date
from sqlalchemy.orm import declarative_base, relationship
from app.handlers.fix.db.models.base import Base
# from ...admin_core.app.handlers import add_new_user


class User(Base):
    __tablename__ = 'User'

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    telegram_id = Column(String(), nullable=False)

    enddate = Column(String(), nullable=True)