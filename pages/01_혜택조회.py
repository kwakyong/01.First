import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.welfare_api import CATEGORIES, get_benefits_by_category

st.set_page_config(page_title="혜택 조회", page_icon="🔍", layout="centered")

st.markdown("""
<style>
    .benefit-card {
        background: #eaf4fb;
        border-radius: 12px;
        padding: 20px 24px;
        margin: 12px 0;
        border-left: 6px solid #2980b9;
    }
    .benefit-title { font-size: 1.25rem; font-weight: bold; color: #1a5276; margin-bottom: 6px; }
    .benefit-desc  { font-size: 1rem; color: #2c3e50; margin-bottom: 8px; }
    .benefit-amount { font-size: 1rem; color: #1e8449; font-weight: bold; }
    .benefit-meta   { font-size: 0.95rem; color: #5d6d7e; margin-top: 4px; }
    .stApp { font-size: 18px; }
</style>
""", unsafe_allow_html=True)

st.title("🔍 복지혜택 조회")
st.write("국가와 지역에서 제공하는 복지혜택 목록입니다.")

category = st.selectbox("📂 분야 선택", ["전체"] + CATEGORIES, index=0)

benefits = get_benefits_by_category(category)
st.write(f"**총 {len(benefits)}개** 혜택이 있습니다.")
st.divider()

for b in benefits:
    st.markdown(f"""
    <div class="benefit-card">
        <div class="benefit-title">{b['name']}</div>
        <div class="benefit-desc">{b['description']}</div>
        <div class="benefit-amount">💰 {b['amount']}</div>
        <div class="benefit-meta">📍 신청처: {b['apply_where']}</div>
        <div class="benefit-meta">👤 대상: {b['age_min']}세 이상 · 소득기준: {b['income_level']}</div>
    </div>
    """, unsafe_allow_html=True)
