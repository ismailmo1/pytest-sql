from uuid import uuid4

from sqlalchemy import Column, Date, Float, String

from db import Base


class Bike(Base):
    """Table to record Bike training sessions"""

    __tablename__ = "bike"

    id = Column(String, primary_key=True, default=uuid4)
    date = Column(Date)
    speed_mph = Column(Float)
    duration_min = Column(Float)


class Treadmill(Base):
    """Reference table for food statistics"""

    __tablename__ = "treadmill"

    id = Column(String, primary_key=True, default=uuid4)
    date = Column(Date)
    speed_mph = Column(Float)
    duration_min = Column(Float)
    incline = Column("incline_%", Float)
