from models.family import FamilyMemberOut
from models.drug import DrugOut
from services.drug_safety import check_drug_safety


class HealthAgent:
    async def run(self, drug: DrugOut, member: FamilyMemberOut) -> dict:
        """Assess medication safety for a specific family member."""
        warnings = check_drug_safety(drug, member)
        advice = self._build_advice(drug, member, warnings)
        return {
            "member_name": member.name,
            "drug_name": drug.name,
            "warnings": warnings,
            "advice": advice,
            "safe": len(warnings) == 0,
        }

    def _build_advice(self, drug: DrugOut, member: FamilyMemberOut, warnings: list[str]) -> str:
        if not warnings:
            return f"{member.name} 服用「{drug.name}」暂无已知风险，请遵医嘱按量服用。"
        lines = [f"{member.name} 服用「{drug.name}」存在以下风险，请谨慎："]
        lines.extend(f"• {w}" for w in warnings)
        lines.append("建议在医生或药师指导下使用。")
        return "\n".join(lines)
