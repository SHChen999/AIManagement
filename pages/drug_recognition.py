import streamlit as st
import httpx
import asyncio

from core.config import get_settings
from agents.thinking import vision_agent_think, knowledge_agent_think

API = get_settings().api_base_url

st.set_page_config(page_title="药品识别", page_icon="📷",     menu_items={
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
.stDivider {
    margin-top: 0.5rem !important;
    margin-bottom: 0.5rem !important;
}
/* 移除 Streamlit 的默认成功提示顶部渲染 */
.element-container:has(.stSuccess) {
    display: none !important;
}
/* 减小 info 框内文字大小 */
.stAlert p {
    font-size: 0.85rem !important;
}
</style>
""", unsafe_allow_html=True)

# 初始化 session_state
if "save_success" not in st.session_state:
    st.session_state["save_success"] = False
if "saved_drug_name" not in st.session_state:
    st.session_state["saved_drug_name"] = ""

st.title("📷 药品识别")
st.markdown("请上传药盒照片，系统将记录药品信息")

uploaded = st.file_uploader("选择药盒照片", type=["jpg", "jpeg", "png"])

if uploaded:
    st.image(uploaded, caption="已上传图片", use_column_width=True)

    drug_name_input = st.text_input(
        "💊 药品名称",
        placeholder="请手动输入药盒上显示的药品名称...",
        help="由于系统暂时无法自动识别图片中的文字，请手动输入药品名称"
    )

    if st.button("🚀 开始识别"):
        if not drug_name_input.strip():
            st.error("请输入药品名称")
            st.stop()

        st.session_state.pop("recognized", None)

        # ===== 多模态信息采集智能体 =====
        st.markdown("---")
        st.markdown("##### 🔍 多模态信息采集智能体")

        vision_box = st.empty()

        async def run_vision_agent():
            first = True
            async for step in vision_agent_think(drug_name_input, num_steps=4):
                if first:
                    vision_box.info(f"💭 {step}")
                    first = False
                else:
                    vision_box.info(f"💭 {step}")
                await asyncio.sleep(0.3)
            vision_box.markdown('<p style="color:green;font-weight:bold;">✅ 图片已保存</p>', unsafe_allow_html=True)

        asyncio.run(run_vision_agent())

        # 交接提示
        st.info("【系统】多模态信息采集智能体工作完毕，正在交接给知识检索智能体...")

        # ===== 知识检索智能体 =====
        st.markdown("##### 📚 知识检索智能体")

        knowledge_box = st.empty()

        async def run_knowledge_agent():
            first = True
            async for step in knowledge_agent_think(drug_name_input, num_steps=5):
                if first:
                    knowledge_box.info(f"💭 {step}")
                    first = False
                else:
                    knowledge_box.info(f"💭 {step}")
                await asyncio.sleep(0.3)
            knowledge_box.markdown('<p style="color:green;font-weight:bold;">✅ 知识检索完成！</p>', unsafe_allow_html=True)

        asyncio.run(run_knowledge_agent())

        # 实际调用API
        try:
            with st.spinner("正在查询数据库..."):
                files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type)}
                payload = {"drug_name": drug_name_input.strip()}

                resp = httpx.post(
                    f"{API}/drugs/recognize",
                    files=files,
                    data=payload,
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()

            st.markdown('<p style="color:green;font-weight:bold;font-size:1.1em;">✅请确认以下信息后保存到药箱</p>', unsafe_allow_html=True)
            st.session_state["recognized"] = data

        except Exception as e:
            st.error(f"❌ 任务失败：{e}")
            st.stop()

if "recognized" in st.session_state or st.session_state.get("save_success"):

    # 保存成功提示（简洁的绿色提示框）
    if st.session_state.get("save_success"):
        saved_name = st.session_state.get('saved_drug_name', '')
        st.success(f"✅ 「{saved_name}」相关信息保存成功！")
        st.session_state["save_success"] = False
        st.session_state.pop("recognized", None)

    elif "recognized" in st.session_state:
        data = st.session_state["recognized"]

        with st.form("confirm_drug", clear_on_submit=True):
            st.subheader("确认药品信息")
            name = st.text_input("药品名称", value=data.get("name", ""))

            st.divider()
            st.markdown("**详细信息**")
            ingredients = st.text_area("成分", value=data.get("ingredients", ""), height=80)
            indications = st.text_area("适应症", value=data.get("indications", ""), height=80)
            contraindications = st.text_area("禁忌症", value=data.get("contraindications", ""), height=80)
            side_effects = st.text_area("副作用", value=data.get("side_effects", ""), height=80)

            submitted = st.form_submit_button("💾 保存到药箱")

        if submitted:
            payload = {
                "name": name,
                "ingredients": ingredients,
                "indications": indications,
                "contraindications": contraindications,
                "side_effects": side_effects,
                "production_date": "",
                "expiry_date": "",
                "image_path": data.get("image_path", ""),
            }
            try:
                r = httpx.post(f"{API}/drugs/", json=payload, timeout=10)
                r.raise_for_status()
                st.session_state["save_success"] = True
                st.session_state["saved_drug_name"] = name
                st.rerun()
            except Exception as e:
                st.error(f"保存失败：{e}")
