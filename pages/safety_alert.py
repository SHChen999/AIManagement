import streamlit as st
import httpx
import asyncio
from datetime import date, datetime
from core.config import get_settings
from agents.thinking import safety_agent_think

API = get_settings().api_base_url


@st.cache_data(ttl=60, show_spinner=False)
def get_members():
    return httpx.get(f"{API}/family/", timeout=10).json()


@st.cache_data(ttl=60, show_spinner=False)
def get_drugs():
    return httpx.get(f"{API}/drugs/", timeout=10).json()


st.set_page_config(page_title="用药安全预警", page_icon="🛡️",     menu_items={
        'Get help': None,
        'Report a bug': None,
        'About': None,
    })

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stApp {
    margin-top: -50px;
    padding-top: 0px;
}
.stFormSubmitButton button {
    background-color: #90EE90 !important;
    color: #000000 !important;
    font-weight: bold !important;
    border: none !important;
}
.stFormSubmitButton button:hover {
    background-color: #7CCD7C !important;
}
.stApp {
    font-family: "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", sans-serif;
}
.stDivider {
    margin-top: 0.5rem !important;
    margin-bottom: 0.5rem !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🛡️ 用药安全预警")
st.markdown("根据家庭成员健康档案，检测用药风险")

with st.spinner("加载数据中..."):
    try:
        members = get_members()
        drugs = get_drugs()
    except Exception as e:
        st.error(f"无法连接后端：{e}")
        st.stop()

if not members:
    st.warning("请先在「家庭档案」中添加家庭成员")
    st.stop()

if not drugs:
    st.warning("请先在「药品识别」中添加药品")
    st.stop()

# 检查过期药品
today = date.today()
expired_drugs = []
expiring_drugs = []
for drug in drugs:
    expiry_str = drug.get("expiry_date", "")
    if expiry_str:
        try:
            expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
            days_left = (expiry_date - today).days
            if days_left < 0:
                expired_drugs.append((drug, abs(days_left)))
            elif days_left <= 30:
                expiring_drugs.append((drug, days_left))
        except ValueError:
            pass

# 显示过期警告
if expired_drugs:
    st.error("🚨 **以下药品已过期，请立即处理！**")
    for drug, days in expired_drugs:
        st.markdown(f"- 🔴 `{drug['name']}` 已过期 **{days}** 天")

if expiring_drugs:
    st.warning("⚠️ **以下药品即将过期**")
    for drug, days in expiring_drugs:
        st.markdown(f"- 🟡 `{drug['name']}` 即将在 **{days}** 天后过期")

member_map = {m["name"]: m["id"] for m in members}
drug_map = {d["name"]: d["id"] for d in drugs}

with st.form("safety_check"):
    member_name = st.selectbox("选择家庭成员", list(member_map.keys()), key="safety_member")
    drug_name = st.selectbox("选择药品", list(drug_map.keys()), key="safety_drug")
    submitted = st.form_submit_button("开始安全检查")

if submitted:
    # 获取成员和药品详情
    member_id = member_map[member_name]
    drug_id = drug_map[drug_name]
    current_member = next((m for m in members if m["id"] == member_id), None)
    current_drug = next((d for d in drugs if d["id"] == drug_id), None)

    st.info("【健康管家智能体】您好！我是您的健康管家，正在准备为您进行用药安全检查...")

    # ===== 健康管家智能体 =====
    st.markdown("---")
    st.markdown("### 🏥 健康管家智能体")

    # 创建一个容器用于流式显示思考过程
    safety_box = st.empty()

    async def run_safety_agent():
        async for step in safety_agent_think(
            member_name=member_name,
            age=current_member.get("age", ""),
            allergies=current_member.get("allergies", ""),
            drug_name=drug_name,
            indications=current_drug.get("indications", ""),
            contraindications=current_drug.get("contraindications", ""),
            num_steps=6,
        ):
            safety_box.info(f"💭 {step}")
            await asyncio.sleep(0.3)
        # 思考过程显示完成后隐藏
        safety_box.empty()

    asyncio.run(run_safety_agent())
    st.success("✅ 安全分析完成！")

    # 先检查药品是否过期
    expiry_warning = ""
    if current_drug:
        expiry_str = current_drug.get("expiry_date", "")
        if expiry_str:
            try:
                expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
                days_left = (expiry_date - today).days
                if days_left < 0:
                    expiry_warning = f"\n\n🚨 **警告：该药品已过期 {abs(days_left)} 天，请勿使用！**"
                elif days_left <= 30:
                    expiry_warning = f"\n\n⚠️ **注意：该药品将在 {days_left} 天后过期**"
            except ValueError:
                pass

    with st.spinner("正在生成安全报告..."):
        try:
            r = httpx.get(
                f"{API}/safety/check",
                params={"drug_id": drug_id, "member_id": member_id},
                timeout=15,
            )
            r.raise_for_status()
            result = r.json()
        except Exception as e:
            st.error(f"检查失败：{e}")
            st.stop()

    st.info("【健康管家智能体】分析完成！以下是您的用药安全报告：")

    if result.get("safe"):
        st.success("✅ 用药安全")
        st.write(result.get("advice", ""))
    else:
        st.error("⚠️ 存在用药风险")
        for w in result.get("warnings", []):
            st.warning(w)
        st.write(result.get("advice", ""))

    if expiry_warning:
        st.markdown(expiry_warning)

    st.info("【健康管家智能体】温馨提示：请遵医嘱用药，如有疑问请咨询专业医生。如需再次检查，请重新选择成员和药品。")
