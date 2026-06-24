"""
迁移脚本：修改 reminders 表的 reminder_time 字段长度
从 String(10) 改为 String(19)，以支持 YYYY-MM-DD HH:MM:SS 格式
"""
import asyncio
from sqlalchemy import text
from core.mysql_db import async_engine


async def migrate():
    async with async_engine.begin() as conn:
        # 修改 reminder_time 字段长度
        await conn.execute(text("""
            ALTER TABLE reminders
            MODIFY COLUMN reminder_time VARCHAR(19) NOT NULL COMMENT 'YYYY-MM-DD HH:MM:SS'
        """))
        print("✅ 字段 reminder_time 已修改为 VARCHAR(19)")


if __name__ == "__main__":
    asyncio.run(migrate())
