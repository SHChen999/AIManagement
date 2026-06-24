from models.drug import DrugOut
from models.family import FamilyMemberOut


# Known drug interaction pairs (drug_a, drug_b) - both lowercase
KNOWN_INTERACTIONS: set[frozenset] = {
    frozenset({"阿司匹林", "华法林"}),
    frozenset({"布洛芬", "阿司匹林"}),
    frozenset({"地高辛", "阿莫西林"}),
    frozenset({"甲硝唑", "华法林"}),
}


def check_drug_safety(drug: DrugOut, member: FamilyMemberOut) -> list[str]:
    warnings = []
    ingredients = [i.strip() for i in drug.ingredients.split(",") if i.strip()]
    allergies = [a.strip() for a in member.allergies.split(",") if a.strip()]
    current_meds = [m.strip() for m in member.current_medications.split(",") if m.strip()]

    # Allergen matching
    for allergen in allergies:
        if any(allergen in ing for ing in ingredients) or allergen in drug.name:
            warnings.append(f"警告：该药品含有 {allergen} 成分，与您的过敏史冲突")

    # Drug interaction detection
    for med in current_meds:
        pair = frozenset({drug.name, med})
        if pair in KNOWN_INTERACTIONS:
            warnings.append(f"注意：该药品与您正在服用的「{med}」可能存在相互作用")

    # Age-based warnings
    if member.age > 65:
        warnings.append("提示：老年人用药请注意减量，建议咨询医生")
    if member.age < 12 and member.age > 0:
        warnings.append("提示：儿童用药请严格按体重计算剂量")

    # Contraindication keyword check against medical history
    if drug.contraindications and member.medical_history:
        history_keywords = [h.strip() for h in member.medical_history.split(",") if h.strip()]
        for kw in history_keywords:
            if kw in drug.contraindications:
                warnings.append(f"警告：您有「{kw}」病史，该药品禁忌症中包含此项")

    return warnings
