import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.welfare_api import CATEGORIES, get_benefits_by_category

st.set_page_config(page_title="혜택 조회", page_icon="🔍", layout="centered")

CATEGORY_COLORS = {
    "노후소득": "#1B4F72",
    "돌봄서비스": "#1A5276",
    "의료": "#145A32",
    "일자리": "#4A235A",
    "장애지원": "#6E2F1A",
    "생활지원": "#7D6608",
    "안전": "#1B2631",
    "기초생활": "#212F3D",
    "여가·문화": "#1F618D",
    "주거": "#784212",
}

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }

    .page-header {
        background: linear-gradient(135deg, #1B2A4A 0%, #2C4A8A 100%);
        border-radius: 16px;
        padding: 32px 28px;
        color: white;
        margin-bottom: 28px;
        box-shadow: 0 4px 20px rgba(27,42,74,0.2);
    }
    .page-header h2 { font-size: 1.7rem; font-weight: 900; margin: 0 0 6px 0; }
    .page-header p  { font-size: 0.95rem; color: #B8CCE8; margin: 0; }

    .benefit-card {
        background: white;
        border-radius: 14px;
        padding: 24px 26px;
        margin: 14px 0;
        box-shadow: 0 2px 16px rgba(27,42,74,0.07);
        border-left: 5px solid #2C4A8A;
        transition: box-shadow 0.2s;
    }
    .benefit-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1B2A4A;
        margin-bottom: 8px;
    }
    .benefit-desc {
        font-size: 0.98rem;
        color: #4A5568;
        line-height: 1.7;
        margin-bottom: 14px;
    }
    .benefit-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 10px;
    }
    .tag {
        display: inline-block;
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 0.82rem;
        font-weight: 600;
    }
    .tag-amount {
        background: #E8F5E9;
        color: #1B5E20;
        border: 1px solid #A5D6A7;
    }
    .tag-target {
        background: #E8EDF4;
        color: #1B2A4A;
        border: 1px solid #B8CCE8;
    }
    .apply-row {
        font-size: 0.88rem;
        color: #7F8C9A;
        margin-top: 6px;
    }
    .count-badge {
        background: #E8EDF4;
        color: #1B2A4A;
        border-radius: 20px;
        padding: 6px 16px;
        font-size: 0.9rem;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <h2>🔍 복지혜택 조회</h2>
    <p>국가와 지역에서 제공하는 복지혜택 전체 목록입니다</p>
</div>
""", unsafe_allow_html=True)

category = st.selectbox("분야 선택", ["전체"] + sorted(CATEGORIES), index=0, label_visibility="collapsed")

benefits = get_benefits_by_category(category)

st.markdown(f'<div class="count-badge">총 {len(benefits)}개 혜택</div>', unsafe_allow_html=True)

for b in benefits:
    color = CATEGORY_COLORS.get(b["category"], "#2C4A8A")
    st.markdown(f"""
    <div class="benefit-card" style="border-left-color: {color};">
        <div class="benefit-title">{b['name']}</div>
        <div class="benefit-desc">{b['description']}</div>
        <div class="benefit-tags">
            <span class="tag tag-amount">💰 {b['amount']}</span>
            <span class="tag tag-target">👤 {b['age_min']}세 이상 · {b['income_level']}</span>
        </div>
        <div class="apply-row">📍 {b['apply_where']}</div>
    </div>
    """, unsafe_allow_html=True)
