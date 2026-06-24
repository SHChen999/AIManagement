from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean
from pydantic import BaseModel
from core.database import Base


class ReminderDB(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, nullable=False)
    drug_name = Column(String(200), nullable=False)
    reminder_time = Column(String(19), nullable=False)   # YYYY-MM-DD HH:MM:SS
    frequency = Column(String(50), default="daily")      # daily / weekly / interval / monthly
    interval_hours = Column(Integer, default=0)
    day_of_month = Column(Integer, default=1)            # 每月几号
    notes = Column(String(500), default="")
    active = Column(Boolean, default=True)


class ReminderCreate(BaseModel):
    member_id: int
    drug_name: str
    reminder_time: str          # YYYY-MM-DD HH:MM:SS
    frequency: str = "daily"
    interval_hours: int = 0
    day_of_month: int = 1
    notes: str = ""


class ReminderOut(ReminderCreate):
    id: int
    active: bool

    class Config:
        from_attributes = True
