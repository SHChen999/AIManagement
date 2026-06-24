from typing import Optional
from sqlalchemy import Column, Integer, String, Text
from pydantic import BaseModel
from core.mysql_db import Base
from core import security


class FamilyMemberDB(Base):
    __tablename__ = "family"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, default=0)
    gender = Column(String(10), default="")
    # AES encrypted fields
    allergies = Column(Text, default="")
    medical_history = Column(Text, default="")
    current_medications = Column(Text, default="")
    # 接收提醒的邮箱（不加密，便于查询）
    email = Column(String(255), default="", nullable=True)


class FamilyMemberCreate(BaseModel):
    name: str
    age: int = 0
    gender: str = ""
    allergies: str = ""        # comma-separated allergens
    medical_history: str = ""
    current_medications: str = ""  # comma-separated drug names
    email: Optional[str] = None   # 接收提醒的邮箱


class FamilyMemberOut(BaseModel):
    id: int
    name: str
    age: int
    gender: str
    allergies: str
    medical_history: str
    current_medications: str
    email: Optional[str] = None

    class Config:
        from_attributes = True


def encrypt_member(data: FamilyMemberCreate) -> dict:
    return {
        "name": data.name,
        "age": data.age,
        "gender": data.gender,
        "allergies": security.encrypt(data.allergies),
        "medical_history": security.encrypt(data.medical_history),
        "current_medications": security.encrypt(data.current_medications),
        "email": data.email or "",
    }


def decrypt_member(db_obj: FamilyMemberDB) -> FamilyMemberOut:
    return FamilyMemberOut(
        id=db_obj.id,
        name=db_obj.name,
        age=db_obj.age,
        gender=db_obj.gender,
        allergies=security.decrypt(db_obj.allergies or ""),
        medical_history=security.decrypt(db_obj.medical_history or ""),
        current_medications=security.decrypt(db_obj.current_medications or ""),
        email=db_obj.email,
    )
