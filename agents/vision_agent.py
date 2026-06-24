"""多模态信息采集智能体：保存药盒图片和用户输入的名称"""
import os
import uuid
import aiofiles
import logging
from typing import Optional
from pydantic import BaseModel

from core.config import get_settings

logger = logging.getLogger(__name__)


class DrugInfo(BaseModel):
    """药品信息"""
    name: str = ""
    ingredients: str = ""
    indications: str = ""
    dosage: str = ""
    image_path: str = ""


class VisionAgent:
    """多模态信息采集智能体：保存图片和用户输入的名称"""

    async def run(self, image_bytes: bytes, user_drug_name: str = "") -> DrugInfo:
        """保存药盒图片，记录用户输入的药品名称"""
        logger.info("【多模态信息采集智能体】正在保存药盒图片...")

        upload_dir = get_settings().uploads_dir
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir, exist_ok=True)

        filename = f"{uuid.uuid4().hex}.jpg"
        image_path = os.path.join(upload_dir, filename)
        
        async with aiofiles.open(image_path, "wb") as f:
            await f.write(image_bytes)
        logger.info(f"【多模态信息采集智能体】图片已保存: {image_path}")
        
        relative_path = f"uploads/{filename}"
        drug_name = user_drug_name.strip() if user_drug_name else ""

        logger.info(f"【多模态信息采集智能体】任务完毕！药品名称: {drug_name}")
        return DrugInfo(
            name=drug_name,
            image_path=relative_path
        )
