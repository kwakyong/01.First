import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.welfare_api import TOP_BENEFITS, REGIONS, CATEGORIES, get_benefits_by_region

st.set_page_config(page_title="혜택 조회", page_icon="🔍", layout="centered")

CATEGORY_COLORS = {
    "노후소득": "#1B4F72", "돌봄서비스": "#1A5276", "의료": "#145A32",
    "일자리": "#4A235A", "장애지원": "#6E2F1A", "생활지원": "#7D6608",
    "안전": "#1B2631", "기초생활": "#212F3D", "여가·문화": "#1F618D",
    "주거": "#784212",
}

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }

    .page-header {
        background: linear-gradient(135deg, #1B2A4A 0%, #2C4A8A 100%);
        border-radius: 16px; padding: 32px 28px; color: white;
        margin-bottom: 28px; box-shadow: 0 4px 20px rgba(27,42,74,0.2);
    }
    .page-header h2 { font-size: 1.7rem; font-weight: 900; margin: 0 0 6px 0; }
    .page-header p  { font-size: 0.95rem; color: #B8CCE8; margin: 0; }

    .section-title {
        font-size: 1.1rem; font-weight: 900; color: #1B2A4A;
        margin: 24px 0 12px 0; padding-left: 12px;
        border-left: 4px solid #2C4A8A;
    }
    .benefit-card {
        background: white; border-radius: 14px; padding: 20px 24px;
        margin: 10px 0; box-shadow: 0 2px 12px rgba(27,42,74,0.07);
        border-left: 5px solid #2C4A8A;
    }
    .top-card {
        background: white; border-radius: 14px; padding: 20px 24px;
        margin: 10px 0; box-shadow: 0 2px 12px rgba(27,42,74,0.07);
        border-left: 5px solid #C9A84C;
    }
    .benefit-title { font-size: 1.1rem; font-weight: 700; color: #1B2A4A; margin-bottom: 6px; }
    .benefit-desc  { font-size: 0.95rem; color: #4A5568; line-height: 1.7; margin-bottom: 10px; }
    .tags { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px; }
    .tag {
        display: inline-block; border-radius: 20px;
        padding: 3px 11px; font-size: 0.8rem; font-weight: 600;
    }
    .tag-amount  { background: #E8F5E9; color: #1B5E20; border: 1px solid #A5D6A7; }
    .tag-target  { background: #E8EDF4; color: #1B2A4A; border: 1px solid #B8CCE8; }
    .tag-region  { background: #FFF8E1; color: #7D6608; border: 1px solid #FFE082; }
    .tag-top     { background: #FFF3E0; color: #E65100; border: 1px solid #FFCC80; }
    .apply-row   { font-size: 0.85rem; color: #7F8C9A; margin-top: 4px; }
    .count-badge {
        background: #E8EDF4; color: #1B2A4A; border-radius: 20px;
        padding: 5px 14px; font-size: 0.88rem; font-weight: 700;
        display: inline-block; margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <h2>🔍 복지혜택 조회</h2>
    <p>국가와 지역에서 제공하는 복지혜택 전체 목록입니다</p>
</div>
""", unsafe_allow_html=True)

# 필터 영역
col1, col2 = st.columns(2)
with col1:
    selected_region = st.selectbox("🗺️ 지역 선택", REGIONS, index=0)
with col2:
    selected_category = st.selectbox("📂 분야 선택", ["전체"] + sorted(CATEGORIES), index=0)

st.divider()

# ─── 추천 서비스 (상단 고정) ───────────────────────────
top_filtered = TOP_BENEFITS
if selected_category != "전체":
    top_filtered = [b for b in TOP_BENEFITS if b["category"] == selected_category]

if top_filtered:
    st.markdown('<div class="section-title">⭐ 추천 서비스</div>', unsafe_allow_html=True)
    for b in top_filtered:
        st.markdown(f"""
        <div class="top-card">
            <div class="benefit-title">{b['name']}</div>
            <div class="benefit-desc">{b['description']}</div>
            <div class="tags">
                <span class="tag tag-top">⭐ 추천</span>
                <span class="tag tag-amount">💰 {b['amount']}</span>
                <span class="tag tag-target">👤 {b['age_min']}세 이상 · {b['income_level']}</span>
                <span class="tag tag-region">🗺️ 전국공통</span>
            </div>
            <div class="apply-row">📍 {b['apply_where']}</div>
        </div>
        """, unsafe_allow_html=True)

# ─── 복지로 API 전체 서비스 ────────────────────────────
st.markdown('<div class="section-title">📋 전체 서비스 목록</div>', unsafe_allow_html=True)

with st.spinner("서비스 목록을 불러오는 중..."):
    api_benefits, debug_msg = get_benefits_by_region(selected_region)

st.caption(debug_msg)

if selected_category != "전체":
    api_benefits = [b for b in api_benefits if b["category"] == selected_category]

st.markdown(f'<div class="count-badge">총 {len(api_benefits)}개</div>', unsafe_allow_html=True)

for b in api_benefits:
    color = CATEGORY_COLORS.get(b["category"], "#2C4A8A")
    url_html = f'<a href="{b["url"]}" target="_blank" style="color:#2C4A8A;font-weight:600;margin-left:8px;">🔗 자세히 보기</a>' if b.get("url") else ""
    region_label = b.get("region", "전국공통")
    st.markdown(f"""
    <div class="benefit-card" style="border-left-color:{color};">
        <div class="benefit-title">{b['name']}</div>
        <div class="benefit-desc">{b['description']}</div>
        <div class="tags">
            <span class="tag tag-region">🗺️ {region_label}</span>
            <span class="tag tag-target">🏢 {b['category']}</span>
        </div>
        <div class="apply-row">📍 {b['apply_where']} {url_html}</div>
    </div>
    """, unsafe_allow_html=True)
