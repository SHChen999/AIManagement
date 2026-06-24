from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from contextlib import asynccontextmanager
from core.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class Base(DeclarativeBase):
    pass

# 创建MySQL数据库引擎（用于medicine知识库）
async_engine = create_async_engine(
    settings.mysql_url, 
    echo=False,
    pool_pre_ping=True,
    pool_size=3,
    max_overflow=5,
    pool_recycle=3600,
    pool_timeout=30,
)
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)


async def init_all_tables():
    """初始化所有表到MySQL数据库（如果不存在）"""
    from models.drug import DrugDB
    from models.family import FamilyMemberDB
    from models.reminder import ReminderDB
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("MySQL mlist、family和reminders表初始化成功")
    except Exception as e:
        logger.warning(f"MySQL表初始化失败: {e}")


async def init_medicine_db():
    """初始化medicine表（如果不存在）- 药品知识库"""
    from models.medicine import Base as MedicineBase
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(MedicineBase.metadata.create_all)
        logger.info("MySQL medicine表初始化成功")
    except Exception as e:
        logger.warning(f"MySQL medicine表初始化失败: {e}")


async def get_medicine_db():
    """获取MySQL数据库会话"""
    async with AsyncSessionLocal() as session:
        yield session


# 兼容性别名
get_db = get_medicine_db


@asynccontextmanager
async def get_medicine_session():
    """上下文管理器方式获取MySQL数据库会话"""
    async with AsyncSessionLocal() as session:
        yield session


# 兼容性别名
init_db = init_all_tables
