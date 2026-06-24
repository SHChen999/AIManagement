"""数据库迁移脚本 - 添加 email 字段"""
import asyncio
from sqlalchemy import text
from core.mysql_db import async_engine


async def migrate():
    async with async_engine.begin() as conn:
        # 检查字段是否已存在
        result = await conn.execute(text("DESCRIBE family"))
        columns = [row[0] for row in result.fetchall()]
        
        if 'email' not in columns:
            print("Adding email column to family table...")
            await conn.execute(text(
                "ALTER TABLE family ADD COLUMN email VARCHAR(255) DEFAULT ''"
            ))
            print("Migration completed!")
        else:
            print("email column already exists, no migration needed")


if __name__ == "__main__":
    asyncio.run(migrate())
