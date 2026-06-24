import streamlit as st
import httpx
from core.config import get_settings

API = get_settings().api_base_url


@st.cache_data(ttl=60, show_spinner=False)
def get_members():
    """获取家庭成员列表（带60秒缓存）"""
    return httpx.get(f"{API}/family/", timeout=10).json()


st.set_page_config(page_title="👨‍👩‍👧 家庭档案管理", page_icon="👨‍👩‍👧",     menu_items={
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
</style>
""", unsafe_allow_html=True)

st.title("👨‍👩‍👧 家庭档案管理")
st.markdown("管理家庭成员健康信息，数据本地加密存储")

with st.spinner("加载成员列表..."):
    try:
        members = get_members()
    except Exception as e:
        st.error(f"无法连接后端：{e}")
        st.stop()

# 添加/编辑成员表单
is_editing = "editing_member_id" in st.session_state and st.session_state.editing_member_id is not None

if is_editing:
    # 编辑模式
    editing_member = next((m for m in members if m["id"] == st.session_state.editing_member_id), None)
    if editing_member:
        with st.expander("✏️ 修改成员信息", expanded=True):
            with st.form("edit_member", clear_on_submit=True):
                name = st.text_input("姓名 *", value=editing_member["name"], key="edit_family_name")
                col1, col2 = st.columns(2)
                with col1:
                    age = st.number_input("年龄", min_value=0, max_value=120, value=editing_member["age"], key="edit_family_age")
                with col2:
                    gender = st.selectbox("性别", ["男", "女", "其他"], index=["男", "女", "其他"].index(editing_member["gender"]) if editing_member["gender"] in ["男", "女", "其他"] else 0, key="edit_family_gender")
                allergies = st.text_input("过敏史（逗号分隔，如：青霉素,花粉）", value=editing_member.get("allergies", "") or "", key="edit_family_allergies")
                medical_history = st.text_input("病史（逗号分隔，如：高血压,糖尿病）", value=editing_member.get("medical_history", "") or "", key="edit_family_history")
                current_medications = st.text_input("正在服用的药物（逗号分隔）", value=editing_member.get("current_medications", "") or "", key="edit_family_meds")
                email = st.text_input("接收提醒邮箱", value=editing_member.get("email") or "", key="edit_family_email", help="设置后将在用药提醒时间收到邮件通知")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    submitted = st.form_submit_button("保存修改")
                with col_btn2:
                    if st.form_submit_button("取消"):
                        st.session_state.editing_member_id = None
                        st.rerun()

                if submitted:
                    if not name:
                        st.error("姓名不能为空")
                    else:
                        payload = {
                            "name": name, "age": age, "gender": gender,
                            "allergies": allergies, "medical_history": medical_history,
                            "current_medications": current_medications,
                            "email": email,
                        }
                        try:
                            r = httpx.put(f"{API}/family/{editing_member['id']}", json=payload, timeout=10)
                            r.raise_for_status()
                            st.cache_data.clear()
                            st.success(f"成员「{name}」信息已更新")
                            st.session_state.editing_member_id = None
                            st.rerun()
                        except Exception as e:
                            st.error(f"修改失败：{e}")
else:
    # 添加模式
    with st.expander("➕ 添加家庭成员", expanded=False):
        with st.form("add_member", clear_on_submit=True):
            name = st.text_input("姓名 *", key="family_name")
            col1, col2 = st.columns(2)
            with col1:
                age = st.number_input("年龄", min_value=0, max_value=120, value=30, key="family_age")
            with col2:
                gender = st.selectbox("性别", ["男", "女", "其他"], key="family_gender")
            allergies = st.text_input("过敏史（逗号分隔，如：青霉素,花粉）", key="family_allergies")
            medical_history = st.text_input("病史（逗号分隔，如：高血压,糖尿病）", key="family_history")
            current_medications = st.text_input("正在服用的药物（逗号分隔）", key="family_meds")
            email = st.text_input("接收提醒邮箱", key="family_email", help="设置后将在用药提醒时间收到邮件通知")
            submitted = st.form_submit_button("保存")

        if submitted:
            if not name:
                st.error("姓名不能为空")
            else:
                payload = {
                    "name": name, "age": age, "gender": gender,
                    "allergies": allergies, "medical_history": medical_history,
                    "current_medications": current_medications,
                    "email": email,
                }
                try:
                    r = httpx.post(f"{API}/family/", json=payload, timeout=10)
                    r.raise_for_status()
                    st.cache_data.clear()
                    st.success(f"成员「{name}」已添加")
                    st.rerun()
                except Exception as e:
                    st.error(f"添加失败：{e}")

st.divider()
st.subheader("家庭成员列表")

if members:
    for m in members:
        with st.expander(f"👤 {m['name']}  {m['age']}岁 · {m['gender']}"):
            st.write(f"**过敏史：** {m.get('allergies', '-') or '-'}")
            st.write(f"**病史：** {m.get('medical_history', '-') or '-'}")
            st.write(f"**正在服药：** {m.get('current_medications', '-') or '-'}")
            email_display = m.get('email') or ''
            if email_display:
                st.write(f"**提醒邮箱：** {email_display} ✅")
            else:
                st.write("**提醒邮箱：** 未设置 ⚠️")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("修改", key=f"edit_m_{m['id']}"):
                    st.session_state.editing_member_id = m["id"]
                    st.rerun()
            with col2:
                if st.button("删除成员", key=f"del_m_{m['id']}"):
                    httpx.delete(f"{API}/family/{m['id']}", timeout=10)
                    st.cache_data.clear()
                    st.rerun()
else:
    st.info("暂无家庭成员，请点击上方添加")
