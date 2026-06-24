import logging
import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# 创建独立的数据库引擎
_db_engine = None
_db_session_factory = None


def _get_db_engine():
    """获取或创建数据库引擎"""
    global _db_engine, _db_session_factory
    if _db_engine is None:
        logger.info("【知识检索智能体】创建数据库引擎...")
        _db_engine = create_async_engine(
            settings.mysql_url,
            echo=False,
            pool_pre_ping=True,
            pool_size=2,
            max_overflow=3,
            connect_args={
                "connect_timeout": 10,
            },
        )
        _db_session_factory = async_sessionmaker(_db_engine, expire_on_commit=False)
        logger.info("【知识检索智能体】数据库引擎创建完成")
    return _db_engine, _db_session_factory


class KnowledgeAgent:
    """知识检索智能体：从MySQL数据库查询药品信息"""

    def __init__(self):
        self.timeout = 30  # 查询超时时间

    async def run(self, drug_name: str) -> dict:
        """根据药品名称从MySQL数据库查询药品权威信息"""
        logger.info(f"【知识检索智能体】开始查询药品: {drug_name}")
        
        try:
            result = await asyncio.wait_for(
                self._query_medicine_db(drug_name),
                timeout=self.timeout
            )
            logger.info(f"【知识检索智能体】任务完毕！")
            return result
            
        except asyncio.TimeoutError:
            logger.error(f"【知识检索智能体】超时（{self.timeout}秒）")
            return self._error_result(drug_name, "查询超时")
            
        except Exception as e:
            logger.error(f"【知识检索智能体】失败: {type(e).__name__}: {e}")
            return self._error_result(drug_name, f"查询失败: {str(e)[:50]}")

    def _error_result(self, drug_name: str, message: str) -> dict:
        return {
            "name": drug_name,
            "ingredients": message,
            "indications": message,
            "contraindications": message,
            "side_effects": message,
        }

    async def _query_medicine_db(self, drug_name: str) -> dict:
        """从MySQL数据库查询药品信息"""
        logger.info(f"【知识检索智能体】正在连接数据库...")
        
        engine, session_factory = _get_db_engine()
        
        async with session_factory() as session:
            logger.info(f"【知识检索智能体】连接成功，执行查询...")
            
            from models.medicine import MedicineDB
            stmt = select(MedicineDB).where(
                MedicineDB.medicine_name.like(f"%{drug_name}%")
            )
            result = await session.execute(stmt)
            drug = result.scalar_one_or_none()

            if drug:
                logger.info(f"【知识检索智能体】找到药品: {drug.medicine_name}")
                return {
                    "name": drug.medicine_name or drug_name,
                    "ingredients": drug.ingredients or "",
                    "indications": drug.indications or "",
                    "contraindications": drug.contraindications or "",
                    "side_effects": drug.side_effects or "",
                }
            else:
                logger.warning(f"【知识检索智能体】未找到: {drug_name}")
                return {
                    "name": drug_name,
                    "ingredients": "未找到该药品",
                    "indications": "未找到该药品",
                    "contraindications": "未找到该药品",
                    "side_effects": "未找到该药品",
                }
