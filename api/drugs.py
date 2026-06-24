import os
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db, AsyncSessionLocal
from models.drug import DrugDB, DrugCreate, DrugOut, DrugUpdate
from models.medicine import MedicineDB
from agents.vision_agent import VisionAgent
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/drugs", tags=["drugs"])


async def query_drug_from_db(drug_name: str) -> dict:
    """从MySQL数据库查询药品详细信息"""
    logger.info("【知识检索智能体】正在连接数据库...")
    
    try:
        async with AsyncSessionLocal() as session:
            logger.info("【知识检索智能体】连接成功，执行查询...")
            
            stmt = select(MedicineDB).where(
                MedicineDB.medicine_name.like(f"%{drug_name}%")
            )
            result = await session.execute(stmt)
            drug = result.scalar_one_or_none()

            if drug:
                logger.info(f"【知识检索智能体】找到药品: {drug.medicine_name}")
                return {
                    "ingredients": drug.ingredients or "",
                    "indications": drug.indications or "",
                    "contraindications": drug.contraindications or "",
                    "side_effects": drug.side_effects or "",
                }
            else:
                logger.warning(f"【知识检索智能体】未找到: {drug_name}")
                return {
                    "ingredients": "未找到该药品",
                    "indications": "未找到该药品",
                    "contraindications": "未找到该药品",
                    "side_effects": "未找到该药品",
                }
    except Exception as e:
        logger.error(f"【知识检索智能体】查询失败: {type(e).__name__}: {e}")
        return {
            "ingredients": "查询失败",
            "indications": "查询失败",
            "contraindications": "查询失败",
            "side_effects": "查询失败",
        }


@router.post("/recognize")
async def recognize_drug(
    file: UploadFile = File(...),
    drug_name: Optional[str] = Form(None)
):
    """药品识别接口：保存图片 + 查询数据库"""
    logger.info("=" * 50)
    logger.info("【多模态信息采集智能体】正在保存药盒图片...")

    # 读取图片
    image_bytes = await file.read()

    # 调用多模态信息采集智能体保存图片
    vision_agent = VisionAgent()
    drug_info = await vision_agent.run(image_bytes, user_drug_name=drug_name or "")

    # 使用用户输入的药品名
    name = drug_name.strip() if drug_name else "未知药品"

    logger.info(f"【多模态信息采集智能体】图片已保存: {drug_info.image_path}")
    logger.info("【知识检索智能体】正在查询数据库...")

    # 查询数据库获取药品信息
    db_result = await query_drug_from_db(name)
    logger.info("【知识检索智能体】任务完毕！")
    logger.info("=" * 50)

    return {
        "name": name,
        "image_path": drug_info.image_path,
        "ingredients": db_result.get("ingredients") or "",
        "indications": db_result.get("indications") or "",
        "contraindications": db_result.get("contraindications") or "",
        "side_effects": db_result.get("side_effects") or "",
    }


@router.post("/", response_model=DrugOut)
async def create_drug(data: DrugCreate, db: AsyncSession = Depends(get_db)):
    drug = DrugDB(**data.model_dump())
    db.add(drug)
    await db.commit()
    await db.refresh(drug)
    return drug


@router.get("/", response_model=list[DrugOut])
async def list_drugs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DrugDB))
    return result.scalars().all()


@router.get("/{drug_id}", response_model=DrugOut)
async def get_drug(drug_id: int, db: AsyncSession = Depends(get_db)):
    drug = await db.get(DrugDB, drug_id)
    if not drug:
        raise HTTPException(status_code=404, detail="药品不存在")
    return drug


@router.patch("/{drug_id}", response_model=DrugOut)
async def update_drug(drug_id: int, data: DrugUpdate, db: AsyncSession = Depends(get_db)):
    drug = await db.get(DrugDB, drug_id)
    if not drug:
        raise HTTPException(status_code=404, detail="药品不存在")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(drug, field, value)
    await db.commit()
    await db.refresh(drug)
    return drug


@router.delete("/{drug_id}")
async def delete_drug(drug_id: int, db: AsyncSession = Depends(get_db)):
    drug = await db.get(DrugDB, drug_id)
    if not drug:
        raise HTTPException(status_code=404, detail="药品不存在")
    await db.delete(drug)
    await db.commit()
    return {"ok": True}
