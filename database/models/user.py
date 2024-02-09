from sqlite3 import Date

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from database.models.base import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    full_name = Column(String)
    register_date = Column(DateTime)
    phone = Column(String, default=None)

    is_block = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)

    is_assistant = Column(Boolean, default=False)
    is_doctor = Column(Boolean, default=False)
    is_nurse = Column(Boolean, default=False)

    # is_nurse = True
    # is_assistant = True

    fio = Column(String, default=None)
    position = Column(String, default=None)
    seniority = Column(DateTime, default=None)
    calculation = Column(Integer, default=0)
