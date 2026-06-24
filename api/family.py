from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from models.family import FamilyMemberDB, FamilyMemberCreate, FamilyMemberOut, encrypt_member, decrypt_member

router = APIRouter(prefix="/family", tags=["family"])


@router.post("/", response_model=FamilyMemberOut)
async def create_member(data: FamilyMemberCreate, db: AsyncSession = Depends(get_db)):
    encrypted = encrypt_member(data)
    member = FamilyMemberDB(**encrypted)
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return decrypt_member(member)


@router.get("/", response_model=list[FamilyMemberOut])
async def list_members(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FamilyMemberDB))
    return [decrypt_member(m) for m in result.scalars().all()]


@router.get("/{member_id}", response_model=FamilyMemberOut)
async def get_member(member_id: int, db: AsyncSession = Depends(get_db)):
    member = await db.get(FamilyMemberDB, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="成员不存在")
    return decrypt_member(member)


@router.put("/{member_id}", response_model=FamilyMemberOut)
async def update_member(member_id: int, data: FamilyMemberCreate, db: AsyncSession = Depends(get_db)):
    member = await db.get(FamilyMemberDB, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="成员不存在")
    encrypted = encrypt_member(data)
    for k, v in encrypted.items():
        setattr(member, k, v)
    await db.commit()
    await db.refresh(member)
    return decrypt_member(member)


@router.delete("/{member_id}")
async def delete_member(member_id: int, db: AsyncSession = Depends(get_db)):
    member = await db.get(FamilyMemberDB, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="成员不存在")
    await db.delete(member)
    await db.commit()
    return {"ok": True}
