from uuid import uuid4

from sqlalchemy import Column, Date, ForeignKey, Integer, String

from db import Base


class FoodConsumption(Base):
    """Table to record food entries"""

    __tablename__ = "food_cons"

    id = Column(String, primary_key=True, default=uuid4)
    food_id = Column(String, ForeignKey("food_ref.id"))
    qty = Column(Integer)
    date = Column(Date)


class FoodReference(Base):
    """Reference table for food statistics"""

    __tablename__ = "food_ref"

    id = Column(String, primary_key=True, default=uuid4)
    name = Column(String)
    kcal = Column("kcal/unit", Integer)
    unit_of_measure = Column(String)
