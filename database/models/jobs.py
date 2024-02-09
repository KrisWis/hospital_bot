from sqlite3 import Date

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from database.models.base import Base


class Jobs(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    doctor_id = Column(Integer)
    second_doctor_id = Column(Integer)
    date = Column(DateTime)

    hours = Column(Integer, default=0)

    second_doctor_hours = Column(Integer, default=0)

    sighting = Column(Integer, default=0)
    optg = Column(Integer, default=0)
    kt = Column(Integer, default=0)
    trg = Column(Integer, default=0)
    blood = Column(Integer, default=0)
    implantation = Column(Integer, default=0)

    doctor_rate = Column(Integer, default=0)
    second_doctor_rate = Column(Integer, default=0)

    nurse_rate = Column(Integer, default=0)
    is_nurse = Column(Boolean, default=False)
