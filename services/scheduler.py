import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select
from core.database import AsyncSessionLocal
from models.reminder import ReminderDB
from models.family import FamilyMemberDB
from services.email import email_service

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

# 存储待确认的提醒
pending_reminders = []

async def _fire_reminder(drug_name: str, member_id: int, notes: str, reminder_id: int):
    logger.info(f"[提醒] 成员ID {member_id} 该服药了：{drug_name}。{notes}")
    
    # 查询成员的邮箱
    member_email = None
    member_name = None
    async with AsyncSessionLocal() as session:
        member = await session.get(FamilyMemberDB, member_id)
        if member:
            member_email = member.email
            member_name = member.name
    
    # 发送邮件提醒
    if member_email:
        success = email_service.send_reminder(
            to_email=member_email,
            member_name=member_name or f"成员{member_id}",
            drug_name=drug_name,
            dosage="",
            notes=notes,
            reminder_time=datetime.now()
        )
        if success:
            logger.info(f"邮件提醒已发送至 {member_email}")
        else:
            logger.warning(f"邮件提醒发送失败")
    else:
        logger.info("成员未设置邮箱，跳过邮件提醒")
    
    # 添加到待确认列表
    pending_reminders.append({
        "reminder_id": reminder_id,
        "member_id": member_id,
        "drug_name": drug_name,
        "notes": notes,
        "time": datetime.now().strftime("%H:%M")
    })


async def load_reminders():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(ReminderDB).where(ReminderDB.active == True))
        reminders = result.scalars().all()
    for r in reminders:
        _schedule_reminder(r)
    logger.info(f"已加载 {len(reminders)} 条提醒任务")


def _schedule_reminder(r: ReminderDB):
    job_id = f"reminder_{r.id}"
    if scheduler.get_job(job_id):
        return
    if r.frequency == "interval" and r.interval_hours > 0:
        trigger = IntervalTrigger(hours=r.interval_hours)
    else:
        # 支持 YYYY-MM-DD HH:MM:SS 和 HH:MM 两种格式
        time_str = r.reminder_time.strip()
        if " " in time_str:
            # 新格式 YYYY-MM-DD HH:MM:SS
            parts = time_str.split(" ")
            if len(parts) >= 2:
                time_part = parts[1]
                hour_str, minute_str = time_part.split(":")[:2]
                hour = int(hour_str)
                minute = int(minute_str)
            else:
                hour, minute = 8, 0
        else:
            # 旧格式 HH:MM
            hour_str, minute_str = time_str.split(":")[:2]
            hour = int(hour_str)
            minute = int(minute_str)
        trigger = CronTrigger(hour=hour, minute=minute)
    scheduler.add_job(
        _fire_reminder,
        trigger=trigger,
        id=job_id,
        kwargs={"drug_name": r.drug_name, "member_id": r.member_id, "notes": r.notes, "reminder_id": r.id},
        replace_existing=True,
    )


def add_reminder_job(r: ReminderDB):
    _schedule_reminder(r)


def remove_reminder_job(reminder_id: int):
    job_id = f"reminder_{reminder_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
