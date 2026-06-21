import streamlit as st
import sys
import os
from collections import defaultdict
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.welfare_api import (
    TOP_BENEFITS, REGIONS, USER_CATEGORIES, TOP_TO_USER_CAT, get_benefits_by_region,
    TOP_YOUTH_BENEFITS, YOUTH_CATEGORIES, YOUTH_TO_USER_CAT, get_youth_benefits_by_region,
)

st.set_page_config(page_title="혜택 조회", page_icon="🔍", layout="centered")

MINISTRY_ICON = {
    "보건복지부": "🏥", "고용노동부": "💼", "행정안전부": "🏛️",
    "국토교통부": "🏠", "여성가족부": "👨‍👩‍👧", "교육부": "📚",
    "문화체육관광부": "🎭", "국가보훈처": "🎖️", "국가보훈부": "🎖️",
    "기획재정부": "💰", "환경부": "🌿", "농림축산식품부": "🌾",
    "중소벤처기업부": "🏢",
}

CAT_ICON_SENIOR = {
    "노후·연금": "💛", "의료·건강": "🏥", "돌봄·요양": "🤝",
    "생활지원": "🛒", "일자리·창업": "💼", "주거": "🏠",
    "장애지원": "♿", "안전·긴급": "🚨", "여가·문화": "🎭", "기타": "📌",
}

CAT_ICON_YOUTH = {
    "학비·장학금": "📚", "생활비지원": "🛒", "주거": "🏠",
    "일자리·취업": "💼", "건강·심리": "🏥", "문화·여가": "🎭",
    "자립지원": "🤝", "창업·금융": "💰", "기타": "📌",
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

    .page-header-youth {
        background: linear-gradient(135deg, #1A3A2A 0%, #2E7D52 100%);
        border-radius: 16px; padding: 32px 28px; color: white;
        margin-bottom: 28px; box-shadow: 0 4px 20px rgba(20,60,40,0.2);
    }
    .page-header-youth h2 { font-size: 1.7rem; font-weight: 900; margin: 0 0 6px 0; }
    .page-header-youth p  { font-size: 0.95rem; color: #A8D8BC; margin: 0; }

    .section-title {
        font-size: 1.1rem; font-weight: 900; color: #1B2A4A;
        margin: 24px 0 12px 0; padding-left: 12px;
        border-left: 4px solid #2C4A8A;
    }
    .section-title-youth {
        font-size: 1.1rem; font-weight: 900; color: #1A3A2A;
        margin: 24px 0 12px 0; padding-left: 12px;
        border-left: 4px solid #2E7D52;
    }
    .benefit-card {
        background: white; border-radius: 14px; padding: 18px 22px;
        margin: 8px 0; box-shadow: 0 2px 12px rgba(27,42,74,0.07);
        border-left: 5px solid #2C4A8A;
    }
    .benefit-card-youth {
        background: white; border-radius: 14px; padding: 18px 22px;
        margin: 8px 0; box-shadow: 0 2px 12px rgba(20,60,40,0.07);
        border-left: 5px solid #2E7D52;
    }
    .top-card {
        background: white; border-radius: 14px; padding: 20px 24px;
        margin: 10px 0; box-shadow: 0 2px 12px rgba(27,42,74,0.07);
        border-left: 5px solid #C9A84C;
    }
    .top-card-youth {
        background: white; border-radius: 14px; padding: 20px 24px;
        margin: 10px 0; box-shadow: 0 2px 12px rgba(20,60,40,0.07);
        border-left: 5px solid #43A047;
    }
    .benefit-title { font-size: 1.05rem; font-weight: 700; color: #1B2A4A; margin-bottom: 6px; }
    .benefit-desc  { font-size: 0.92rem; color: #4A5568; line-height: 1.7; margin-bottom: 10px; }
    .tags { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px; }
    .tag {
        display: inline-block; border-radius: 20px;
        padding: 3px 11px; font-size: 0.78rem; font-weight: 600;
    }
    .tag-amount  { background: #E8F5E9; color: #1B5E20; border: 1px solid #A5D6A7; }
    .tag-target  { background: #E8EDF4; color: #1B2A4A; border: 1px solid #B8CCE8; }
    .tag-region  { background: #FFF8E1; color: #7D6608; border: 1px solid #FFE082; }
    .tag-top     { background: #FFF3E0; color: #E65100; border: 1px solid #FFCC80; }
    .tag-youth   { background: #E8F5E8; color: #1B5E20; border: 1px solid #81C784; }
    .tag-cat     { background: #EDE7F6; color: #4527A0; border: 1px solid #CE93D8; }
    .apply-row   { font-size: 0.83rem; color: #7F8C9A; margin-top: 4px; }
    .count-badge {
        background: #E8EDF4; color: #1B2A4A; border-radius: 20px;
        padding: 5px 14px; font-size: 0.88rem; font-weight: 700;
        display: inline-block; margin-bottom: 12px;
    }
    .no-result {
        background: #F4F6F9; border-radius: 12px; padding: 28px;
        text-align: center; color: #7F8C9A; font-size: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ─── 대상 그룹 확인 ─────────────────────────────────────
is_youth = st.session_state.get("target_group", "senior") == "youth"

if is_youth:
    st.markdown("""
    <div class="page-header-youth">
        <h2>🎓 청소년·대학생 복지혜택 조회</h2>
        <p>만 15~24세 청소년·대학생을 위한 복지혜택 목록입니다</p>
    </div>
    """, unsafe_allow_html=True)
    CAT_ICON = CAT_ICON_YOUTH
    top_benefits = TOP_YOUTH_BENEFITS
    user_categories = YOUTH_CATEGORIES
    top_to_user_cat = YOUTH_TO_USER_CAT
    section_cls = "section-title-youth"
    top_card_cls = "top-card-youth"
    benefit_card_cls = "benefit-card-youth"
    top_tag = "🎓 청소년·대학생"
else:
    st.markdown("""
    <div class="page-header">
        <h2>🔍 복지혜택 조회</h2>
        <p>국가와 지역에서 제공하는 복지혜택 전체 목록입니다</p>
    </div>
    """, unsafe_allow_html=True)
    CAT_ICON = CAT_ICON_SENIOR
    top_benefits = TOP_BENEFITS
    user_categories = USER_CATEGORIES
    top_to_user_cat = TOP_TO_USER_CAT
    section_cls = "section-title"
    top_card_cls = "top-card"
    benefit_card_cls = "benefit-card"
    top_tag = "⭐ 추천"

# ─── API 로드 (캐시) ──────────────────────────────────
@st.cache_data(ttl=3600)
def _load_senior_benefits(region: str):
    return get_benefits_by_region(region)

@st.cache_data(ttl=3600)
def _load_youth_benefits(region: str):
    return get_youth_benefits_by_region(region)

# 필터 1행: 지역 | 카테고리
col1, col2 = st.columns(2)
with col1:
    selected_region = st.selectbox("🗺️ 지역 선택", REGIONS, index=0)
with col2:
    cat_options = ["전체"] + user_categories
    selected_cat = st.selectbox("📂 분야 선택", cat_options, index=0)

# 필터 2행: 키워드 검색
search_query = st.text_input(
    "검색",
    placeholder="🔍  서비스명 또는 내용으로 검색하세요  예) 장학금, 월세, 취업",
    label_visibility="collapsed"
)

# 데이터 로드
if is_youth:
    all_api_benefits, debug_msg = _load_youth_benefits(selected_region)
else:
    all_api_benefits, debug_msg = _load_senior_benefits(selected_region)
st.caption(debug_msg)
st.divider()

# ─── 추천 / 주요 서비스 ───────────────────────────────
top_filtered = top_benefits
if selected_cat != "전체":
    top_filtered = [b for b in top_filtered
                    if top_to_user_cat.get(b["category"]) == selected_cat]
if search_query:
    q = search_query.lower()
    top_filtered = [b for b in top_filtered
                    if q in b["name"].lower() or q in b.get("description", "").lower()]

if top_filtered:
    label = "🎓 주요 청소년·대학생 혜택" if is_youth else "⭐ 추천 서비스"
    st.markdown(f'<div class="{section_cls}">{label}</div>', unsafe_allow_html=True)
    for b in top_filtered:
        user_cat = top_to_user_cat.get(b["category"], "기타")
        cat_icon = CAT_ICON.get(user_cat, "📌")
        age_text = f"{b['age_min']}~{b.get('age_max', '')}세" if is_youth and b.get("age_max") else f"{b['age_min']}세 이상"
        st.markdown(f"""
        <div class="{top_card_cls}">
            <div class="benefit-title">{b['name']}</div>
            <div class="benefit-desc">{b['description']}</div>
            <div class="tags">
                <span class="tag {'tag-youth' if is_youth else 'tag-top'}">{top_tag}</span>
                <span class="tag tag-cat">{cat_icon} {user_cat}</span>
                <span class="tag tag-amount">💰 {b['amount']}</span>
                <span class="tag tag-target">👤 {age_text} · {b['income_level']}</span>
                <span class="tag tag-region">🗺️ 전국공통</span>
            </div>
            <div class="apply-row">📍 {b['apply_where']}</div>
        </div>
        """, unsafe_allow_html=True)

# ─── API 전체 서비스 ────────────────────────────────────
api_label = "📋 복지로 API 청소년 관련 서비스" if is_youth else "📋 전체 서비스 목록"
st.markdown(f'<div class="{section_cls}">{api_label}</div>', unsafe_allow_html=True)

api_benefits = all_api_benefits
if selected_cat != "전체":
    api_benefits = [b for b in api_benefits if b.get("user_category") == selected_cat]
if search_query:
    q = search_query.lower()
    api_benefits = [b for b in api_benefits
                    if q in b["name"].lower() or q in b.get("description", "").lower()]

grouped = defaultdict(list)
for b in api_benefits:
    grouped[b["category"]].append(b)

st.markdown(
    f'<div class="count-badge">총 {len(api_benefits)}개 서비스 · {len(grouped)}개 기관</div>',
    unsafe_allow_html=True
)

if not api_benefits:
    st.markdown(
        '<div class="no-result">🔎 검색 결과가 없습니다. 다른 키워드나 분야를 선택해 보세요.</div>',
        unsafe_allow_html=True
    )
else:
    for category in sorted(grouped.keys()):
        items = grouped[category]
        icon = MINISTRY_ICON.get(category, "🏢")
        with st.expander(f"{icon} {category}  —  {len(items)}개 서비스", expanded=False):
            for b in items:
                url_html = (
                    f'<a href="{b["url"]}" target="_blank" '
                    f'style="color:#2C4A8A;font-weight:600;margin-left:8px;">🔗 자세히 보기</a>'
                    if b.get("url") else ""
                )
                region_label = b.get("region", "전국공통")
                user_cat = b.get("user_category", "기타")
                cat_icon = CAT_ICON.get(user_cat, "📌")
                st.markdown(f"""
                <div class="{benefit_card_cls}">
                    <div class="benefit-title">{b['name']}</div>
                    <div class="benefit-desc">{b['description']}</div>
                    <div class="tags">
                        <span class="tag tag-cat">{cat_icon} {user_cat}</span>
                        <span class="tag tag-region">🗺️ {region_label}</span>
                    </div>
                    <div class="apply-row">📍 {b['apply_where']} {url_html}</div>
                </div>
                """, unsafe_allow_html=True)
