from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from core.mysql_db import init_all_tables, init_medicine_db
from core.config import get_settings
from api import drugs, family, reminders, safety, stream
from services.scheduler import scheduler, load_reminders

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 初始化用户数据表（mlist, family）
    await init_all_tables()
    # 初始化药品知识库表（medicine）
    await init_medicine_db()
    # 启动提醒调度器
    await load_reminders()
    scheduler.start()
    logger.info("提醒调度器已启动")
    yield
    # 关闭调度器
    scheduler.shutdown()


app = FastAPI(title="家庭药箱智能管家", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(drugs.router)
app.include_router(family.router)
app.include_router(reminders.router)
app.include_router(safety.router)
app.include_router(stream.router)

# 挂载静态文件目录，提供图片访问服务
uploads_dir = get_settings().uploads_dir
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")


@app.get("/")
async def root():
    return {"message": "家庭药箱智能管家 API 运行中"}
