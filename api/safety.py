from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from models.drug import DrugDB
from models.family import FamilyMemberDB, decrypt_member
from agents.health_agent import HealthAgent

router = APIRouter(prefix="/safety", tags=["safety"])
health_agent = HealthAgent()


@router.get("/check")
async def check_safety(drug_id: int, member_id: int, db: AsyncSession = Depends(get_db)):
    drug = await db.get(DrugDB, drug_id)
    if not drug:
        raise HTTPException(status_code=404, detail="药品不存在")
    member_db = await db.get(FamilyMemberDB, member_id)
    if not member_db:
        raise HTTPException(status_code=404, detail="成员不存在")
    member = decrypt_member(member_db)
    # Build DrugOut-compatible object
    from models.drug import DrugOut
    drug_out = DrugOut.model_validate(drug)
    return await health_agent.run(drug_out, member)
