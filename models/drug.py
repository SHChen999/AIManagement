from datetime import date
from typing import Optional
from sqlalchemy import Column, Integer, String, Date, Text
from pydantic import BaseModel
from core.mysql_db import Base


class DrugDB(Base):
    __tablename__ = "mlist"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    ingredients = Column(Text, default="")
    indications = Column(Text, default="")
    contraindications = Column(Text, default="")
    side_effects = Column(Text, default="")
    production_date = Column(String(20), default="")
    expiry_date = Column(String(20), default="")
    image_path = Column(String(500), default="")


class DrugCreate(BaseModel):
    name: str
    ingredients: str = ""
    indications: str = ""
    contraindications: str = ""
    side_effects: str = ""
    production_date: str = ""
    expiry_date: str = ""
    image_path: str = ""


class DrugOut(DrugCreate):
    id: int

    class Config:
        from_attributes = True


class DrugUpdate(BaseModel):
    name: Optional[str] = None
    ingredients: Optional[str] = None
    indications: Optional[str] = None
    contraindications: Optional[str] = None
    side_effects: Optional[str] = None
    production_date: Optional[str] = None
    expiry_date: Optional[str] = None
    image_path: Optional[str] = None
