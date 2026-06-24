import locale
import os
os.environ['LANG'] = 'zh_CN.UTF-8'
locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')

import streamlit as st

st.set_page_config(
    page_title="💊 家庭药箱智能管家",
    page_icon="💊",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        'Get help': None,
        'Report a bug': None,
        'About': None,
    }
)

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp {
        margin-top: -50px;
        padding-top: 0px;
    }
    .stApp > div:first-child {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    .stButton > button {
        width: 100%;
        height: 5rem;
        font-size: 1rem;
        border-radius: 12px;
        text-align: left;
        padding: 0.8rem 1rem;
    }
    h1 { font-size: 1.3rem; }
</style>
""", unsafe_allow_html=True)

st.title("💊 家庭药箱智能管家")
st.markdown("---")
st.markdown("""
<style>
    section[data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

pages_config = [
    ("📷 药品识别", "pages/drug_recognition.py", "拍照识别药品信息"),
    ("👨‍👩‍👧 家庭档案", "pages/family_profile.py", "管理家庭成员健康信息"),
    ("⏰ 用药提醒", "pages/medication_reminder.py", "定时提醒按时服药"),
    ("🛡️ 安全预警", "pages/safety_alert.py", "个性化用药安全检查"),
    ("🗄️ 药箱清单", "pages/medicine_inventory.py", "查看药箱中所有药品"),
]

for i in range(0, 5, 2):
    cols = st.columns(2)
    
    with cols[0]:
        title, path, desc = pages_config[i]
        if st.button(f"**{title}**\n{desc}", key=f"card_{i}"):
            st.switch_page(path)
    
    if i + 1 < len(pages_config):
        with cols[1]:
            title, path, desc = pages_config[i + 1]
            if st.button(f"**{title}**\n{desc}", key=f"card_{i+1}"):
                st.switch_page(path)
