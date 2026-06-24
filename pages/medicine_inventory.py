import os
from datetime import date, datetime

import httpx
import streamlit as st

from core.config import get_settings

API = get_settings().api_base_url


@st.cache_data(ttl=60, show_spinner=False)
def get_drugs():
    """获取药品列表（带60秒缓存）"""
    return httpx.get(f"{API}/drugs/", timeout=10).json()


st.set_page_config(page_title="药箱清单", page_icon="🗄️", layout="centered",     menu_items={
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

st.title("🗄️ 药箱清单")
st.markdown("管理家庭药箱中的所有药品")

with st.spinner("加载数据中..."):
    try:
        drugs = get_drugs()
    except Exception as e:
        st.error(f"无法连接后端：{e}")
        st.stop()

if not drugs:
    st.info("药箱暂无药品，请前往「药品识别」页面添加药品。")
    st.stop()

st.divider()
st.markdown(f"<p style='text-align:center;color:#000;'>共 {len(drugs)} 种药品</p>", unsafe_allow_html=True)

today = date.today()

# 渲染药品列表
for idx, drug in enumerate(drugs, 1):
    expiry_str = drug.get("expiry_date", "")
    production_str = drug.get("production_date", "")
    days_left = None
    if expiry_str:
        try:
            expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
            days_left = (expiry_date - today).days
        except ValueError:
            pass

    # 状态
    if days_left is None:
        status_text = "未设置有效期"
        status_emoji = "⚪"
    elif days_left < 0:
        status_text = f"已过期 {abs(days_left)} 天"
        status_emoji = "🔴"
    elif days_left <= 30:
        status_text = f"即将过期 {days_left} 天"
        status_emoji = "🟡"
    else:
        status_text = f"有效 {days_left} 天"
        status_emoji = "🟢"

    # 药品卡片
    with st.container():
        # 编号放图片上方
        st.markdown(f"<div style='font-size:1rem;font-weight:bold;color:#667eea;'>No.{idx}</div>", unsafe_allow_html=True)
        
        col_img, col_info = st.columns([1.2, 2.8])
        
        with col_img:
            image_path = drug.get("image_path", "")
            if image_path:
                # 将相对路径转换为URL
                filename = os.path.basename(image_path)
                image_url = f"{API}/uploads/{filename}"
                st.image(image_url, width=80)
            else:
                st.markdown("<div style='font-size:3rem;text-align:center;'>💊</div>", unsafe_allow_html=True)
            # 药品名称显示在图片下方
            st.markdown(f"**{drug.get('name', '未知药品')}**")
            # 删除按钮
            if st.button("🗑️ 删除", key=f"delete_{drug['id']}"):
                try:
                    httpx.delete(f"{API}/drugs/{drug['id']}", timeout=10)
                    st.cache_data.clear()
                    st.success(f"「{drug.get('name', '该药品')}」已删除！")
                    st.rerun()
                except Exception as e:
                    st.error(f"删除失败：{e}")
        
        with col_info:
            st.markdown(f"{status_emoji} {status_text}")
            
            # 有效期设置
            with st.expander("📅 设置有效期", expanded=False):
                with st.form(f"date_form_{drug['id']}"):
                    new_prod = st.date_input(
                        "生产日期",
                        value=datetime.strptime(production_str, "%Y-%m-%d").date() if production_str else today,
                        key=f"prod_{drug['id']}"
                    )
                    new_exp = st.date_input(
                        "失效日期",
                        value=datetime.strptime(expiry_str, "%Y-%m-%d").date() if expiry_str else today,
                        key=f"exp_{drug['id']}"
                    )
                    
                    save_date = st.form_submit_button("💾 保存日期", use_container_width=True)

                if save_date:
                    new_days = (new_exp - today).days
                    try:
                        r = httpx.patch(
                            f"{API}/drugs/{drug['id']}",
                            json={
                                "production_date": str(new_prod),
                                "expiry_date": str(new_exp),
                            },
                            timeout=10,
                        )
                        r.raise_for_status()
                        st.cache_data.clear()
                        if new_days > 0:
                            st.success(f"已更新！还剩 **{new_days}** 天")
                        else:
                            st.warning(f"已更新！⚠️ 已过期 {abs(new_days)} 天")
                        st.rerun()
                    except Exception as e:
                        st.error(f"更新失败：{e}")

    # 药品详情
    with st.expander("📋 查看详情"):
        indications = drug.get('indications', '-') or '-'
        if indications and indications != '-':
            st.markdown("**💉 适应症**")
            st.code(indications)
        
        contraindications = drug.get('contraindications', '-') or '-'
        if contraindications and contraindications != '-':
            st.markdown("**⚠️ 禁忌症**")
            st.code(contraindications)
        
        side_effects = drug.get('side_effects', '-') or '-'
        if side_effects and side_effects != '-':
            st.markdown("**🤒 副作用**")
            st.code(side_effects)
        
        ingredients = drug.get('ingredients', '-') or '-'
        if ingredients and ingredients != '-':
            st.markdown("**💊 成分**")
            st.code(ingredients)

    st.divider()
