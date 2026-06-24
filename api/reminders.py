from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from models.reminder import ReminderDB, ReminderCreate, ReminderOut
from services.scheduler import add_reminder_job, remove_reminder_job, pending_reminders

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.post("/", response_model=ReminderOut)
async def create_reminder(data: ReminderCreate, db: AsyncSession = Depends(get_db)):
    reminder = ReminderDB(**data.model_dump())
    db.add(reminder)
    await db.commit()
    await db.refresh(reminder)
    add_reminder_job(reminder)
    return reminder


@router.get("/", response_model=list[ReminderOut])
async def list_reminders(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ReminderDB))
    return result.scalars().all()


@router.delete("/{reminder_id}")
async def delete_reminder(reminder_id: int, db: AsyncSession = Depends(get_db)):
    reminder = await db.get(ReminderDB, reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail="提醒不存在")
    remove_reminder_job(reminder_id)
    await db.delete(reminder)
    await db.commit()
    return {"ok": True}


@router.patch("/{reminder_id}/toggle", response_model=ReminderOut)
async def toggle_reminder(reminder_id: int, db: AsyncSession = Depends(get_db)):
    reminder = await db.get(ReminderDB, reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail="提醒不存在")
    reminder.active = not reminder.active
    if reminder.active:
        add_reminder_job(reminder)
    else:
        remove_reminder_job(reminder_id)
    await db.commit()
    await db.refresh(reminder)
    return reminder


@router.put("/{reminder_id}", response_model=ReminderOut)
async def update_reminder(reminder_id: int, data: ReminderCreate, db: AsyncSession = Depends(get_db)):
    reminder = await db.get(ReminderDB, reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail="提醒不存在")
    remove_reminder_job(reminder_id)
    for key, value in data.model_dump().items():
        setattr(reminder, key, value)
    await db.commit()
    await db.refresh(reminder)
    if reminder.active:
        add_reminder_job(reminder)
    return reminder


@router.get("/pending")
async def get_pending_reminders():
    """获取待确认的提醒"""
    return pending_reminders


@router.post("/acknowledge/{reminder_id}")
async def acknowledge_reminder(reminder_id: int):
    """确认提醒"""
    global pending_reminders
    pending_reminders = [r for r in pending_reminders if r.get("reminder_id") != reminder_id]
    return {"ok": True}
