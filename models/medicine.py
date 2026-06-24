from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class MedicineDB(Base):
    """MySQL数据库中的药品知识表，对应m数据库下的medicine表"""
    __tablename__ = "medicine"

    id = Column(Integer, primary_key=True, index=True)
    medicine_name = Column(String(100), nullable=False, index=True, comment="药品名称（含常见商品名）")
    ingredients = Column(Text, nullable=False, comment="主要成分")
    indications = Column(Text, nullable=False, comment="适应症")
    contraindications = Column(Text, nullable=False, comment="禁忌症")
    side_effects = Column(Text, nullable=False, comment="常见副作用")
