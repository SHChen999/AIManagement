import streamlit as st
import httpx
from datetime import datetime, date, time
from core.config import get_settings

API = get_settings().api_base_url


@st.cache_data(ttl=60, show_spinner=False)
def get_members():
    return httpx.get(f"{API}/family/", timeout=10).json()


@st.cache_data(ttl=60, show_spinner=False)
def get_drugs():
    return httpx.get(f"{API}/drugs/", timeout=10).json()


@st.cache_data(ttl=60, show_spinner=False)
def get_reminders():
    return httpx.get(f"{API}/reminders/", timeout=10).json()


st.set_page_config(page_title="用药提醒", page_icon="⏰",     menu_items={
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

st.title("⏰ 用药提醒")
st.markdown("设置定时提醒，按时服药不遗漏")

with st.spinner("加载数据中..."):
    try:
        members = get_members()
        drugs = get_drugs()
        reminders = get_reminders()
    except Exception as e:
        st.error(f"无法连接后端：{e}")
        st.stop()

if not members:
    st.warning("请先在「家庭档案」中添加家庭成员")
    st.stop()

if not drugs:
    st.warning("请先在「药品识别」中添加药品")
    st.stop()

member_map = {m["name"]: m["id"] for m in members}
drug_names = [d["name"] for d in drugs]
member_id_map = {m["id"]: m["name"] for m in members}

# 判断是添加模式还是编辑模式
is_editing = "edit_reminder_id" in st.session_state and st.session_state.edit_reminder_id is not None
editing_reminder = None
if is_editing:
    editing_reminder = next((r for r in reminders if r["id"] == st.session_state.edit_reminder_id), None)

if is_editing and editing_reminder:
    # 编辑模式
    with st.expander("✏️ 修改提醒", expanded=True):
        with st.form("edit_reminder", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                member_idx = list(member_map.keys()).index(editing_reminder.get("member_name", list(member_map.keys())[0])) if editing_reminder.get("member_name") in member_map else 0
                member_name = st.selectbox("家庭成员", list(member_map.keys()), index=member_idx, key="edit_reminder_member")
            with col2:
                drug_idx = drug_names.index(editing_reminder["drug_name"]) if editing_reminder["drug_name"] in drug_names else 0
                drug_name = st.selectbox("药品", drug_names, index=drug_idx, key="edit_reminder_drug")

            # 解析已保存的时间字符串
            saved_time = editing_reminder.get("reminder_time", "")
            if saved_time:
                try:
                    dt = datetime.strptime(saved_time, "%Y-%m-%d %H:%M:%S")
                    default_edit_date = dt.date()
                    default_edit_hour = dt.hour
                    default_edit_minute = dt.minute
                except:
                    default_edit_date = date.today()
                    default_edit_hour = 8
                    default_edit_minute = 0
            else:
                default_edit_date = date.today()
                default_edit_hour = 8
                default_edit_minute = 0

            # 年月日时分秒选择
            st.markdown("**提醒时间**")
            col_date1, col_date2, col_date3 = st.columns(3)
            with col_date1:
                edit_reminder_date = st.date_input("日期", value=default_edit_date, key="edit_reminder_date")
            with col_date2:
                edit_reminder_hour = st.selectbox("时", list(range(24)), index=default_edit_hour, key="edit_reminder_hour")
            with col_date3:
                edit_reminder_minute = st.selectbox("分", list(range(60)), index=default_edit_minute, key="edit_reminder_minute")

            freq_map = {"每日": "daily", "每周": "weekly", "间隔": "interval", "每月": "monthly"}
            freq_idx = list(freq_map.values()).index(editing_reminder.get("frequency", "daily")) if editing_reminder.get("frequency") in freq_map else 0
            frequency = st.selectbox("提醒频率", ["每日", "每周", "间隔", "每月"], index=freq_idx, key="edit_reminder_frequency")

            interval_hours = 0
            day_of_month = 1
            if frequency == "间隔":
                interval_hours = st.number_input("间隔小时数", min_value=1, max_value=72, value=editing_reminder.get("interval_hours", 8), key="edit_reminder_interval")
            elif frequency == "每月":
                day_of_month = st.number_input("每月几号", min_value=1, max_value=28, value=editing_reminder.get("day_of_month", 1), key="edit_reminder_day")

            notes = st.text_input("备注（如：饭后服用，每次1粒）", value=editing_reminder.get("notes", ""), key="edit_reminder_notes")

            col_a, col_b = st.columns(2)
            with col_a:
                enable_notification = st.checkbox("启用提醒", value=editing_reminder.get("active", True), key="edit_reminder_enable")

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submitted = st.form_submit_button("保存修改")
            with col_btn2:
                if st.form_submit_button("取消"):
                    st.session_state.edit_reminder_id = None
                    st.rerun()

            if submitted:
                import re
                # 构建完整的时间字符串 格式：YYYY-MM-DD HH:MM:SS
                reminder_time_str = f"{edit_reminder_date} {edit_reminder_hour:02d}:{edit_reminder_minute:02d}:00"

                payload = {
                    "member_id": member_map[member_name],
                    "drug_name": drug_name,
                    "reminder_time": reminder_time_str,
                    "frequency": freq_map[frequency],
                    "interval_hours": interval_hours,
                    "day_of_month": day_of_month,
                    "notes": notes,
                    "active": enable_notification,
                }
                try:
                    r = httpx.put(f"{API}/reminders/{editing_reminder['id']}", json=payload, timeout=10)
                    r.raise_for_status()
                    st.cache_data.clear()
                    st.success("提醒已修改！")
                    st.session_state.edit_reminder_id = None
                    st.rerun()
                except Exception as e:
                    st.error(f"修改失败：{e}")
else:
    # 添加模式
    with st.expander("➕ 添加用药提醒", expanded=True):
        with st.form("add_reminder", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                member_name = st.selectbox("家庭成员", list(member_map.keys()), index=0, key="reminder_member")
            with col2:
                drug_name = st.selectbox("药品", drug_names, index=0, key="reminder_drug")

            # 年月日时分秒选择
            st.markdown("**提醒时间**")
            col_date1, col_date2, col_date3 = st.columns(3)
            with col_date1:
                reminder_date = st.date_input("日期", value=date.today(), key="reminder_date")
            with col_date2:
                reminder_hour = st.selectbox("时", list(range(24)), index=8, key="reminder_hour")
            with col_date3:
                reminder_minute = st.selectbox("分", list(range(60)), index=0, key="reminder_minute")

            frequency = st.selectbox("提醒频率", ["每日", "每周", "间隔", "每月"], index=0, key="reminder_frequency")

            interval_hours = 0
            day_of_month = 1
            if frequency == "间隔":
                interval_hours = st.number_input("间隔小时数", min_value=1, max_value=72, value=8, key="reminder_interval")
            elif frequency == "每月":
                day_of_month = st.number_input("每月几号", min_value=1, max_value=28, value=1, key="reminder_day")

            notes = st.text_input("备注（如：饭后服用，每次1粒）", key="reminder_notes")

            col_a, col_b = st.columns(2)
            with col_a:
                enable_notification = st.checkbox("启用提醒", value=True, key="reminder_enable")

            submitted = st.form_submit_button("保存提醒")

        if submitted:
            import re
            # 构建完整的时间字符串 格式：YYYY-MM-DD HH:MM:SS
            reminder_time_str = f"{reminder_date} {reminder_hour:02d}:{reminder_minute:02d}:00"

            payload = {
                "member_id": member_map[member_name],
                "drug_name": drug_name,
                "reminder_time": reminder_time_str,
                "frequency": {"每日": "daily", "每周": "weekly", "间隔": "interval", "每月": "monthly"}[frequency],
                "interval_hours": interval_hours,
                "day_of_month": day_of_month,
                "notes": notes,
                "active": enable_notification,
            }
            try:
                r = httpx.post(f"{API}/reminders/", json=payload, timeout=10)
                r.raise_for_status()
                st.cache_data.clear()
                st.success("提醒已设置成功！")
                st.rerun()
            except Exception as e:
                st.error(f"设置失败：{e}")

st.divider()

# 提醒列表
st.subheader("📋 提醒列表")

if reminders:
    active_count = sum(1 for r in reminders if r["active"])
    st.caption(f"共 {len(reminders)} 条提醒，其中 {active_count} 条启用中")

    # 创建成员邮箱映射
    member_email_map = {m["id"]: m.get("email") for m in members}

    for r in reminders:
        status = "✅ 启用" if r["active"] else "⏸️ 暂停"
        mname = member_id_map.get(r["member_id"], f"ID:{r['member_id']}")
        freq_display = {"daily": "每日", "weekly": "每周", "interval": "间隔", "monthly": "每月"}.get(r["frequency"], r["frequency"])
        member_email = member_email_map.get(r["member_id"])
        email_status = f"📧 {member_email}" if member_email else "⚠️ 未设邮箱"

        with st.expander(f"{status} · {mname} · {r['drug_name']} · {r['reminder_time']}"):
            st.write(f"**成员：** {mname}")
            st.write(f"**邮箱：** {email_status}")
            st.write(f"**药品：** {r['drug_name']}")
            st.write(f"**提醒时间：** {r['reminder_time']}")
            st.write(f"**频率：** {freq_display}")
            if r["interval_hours"]:
                st.write(f"**间隔：** {r['interval_hours']} 小时")
            st.write(f"**备注：** {r.get('notes', '-') or '-'}")
            st.write(f"**状态：** {status}")

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("启用/暂停", key=f"tog_{r['id']}"):
                    httpx.patch(f"{API}/reminders/{r['id']}/toggle", timeout=10)
                    st.cache_data.clear()
                    st.rerun()
            with col2:
                if st.button("修改", key=f"edit_r_{r['id']}"):
                    st.session_state.edit_reminder_id = r["id"]
                    st.rerun()
            with col3:
                if st.button("删除", key=f"del_r_{r['id']}"):
                    httpx.delete(f"{API}/reminders/{r['id']}", timeout=10)
                    st.cache_data.clear()
                    st.rerun()
else:
    st.info("暂无提醒，请点击上方添加")
