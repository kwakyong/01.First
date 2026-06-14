import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.welfare_api import get_benefits_by_age
from utils.claude_client import check_eligibility
from utils.profile_manager import save_profile, load_profile, delete_profile

st.set_page_config(page_title="자격 확인", page_icon="✅", layout="centered")

st.markdown("""
<style>
    .stApp { font-size: 18px; }
    .result-box {
        background: #f4f6f7;
        border-radius: 10px;
        padding: 16px 20px;
        color: #1a1a2e;
        font-size: 1rem;
        line-height: 1.7;
        border: 1px solid #d5d8dc;
    }
    .saved-badge {
        background: #d5f5e3;
        color: #1e8449;
        border-radius: 8px;
        padding: 6px 14px;
        font-size: 0.95rem;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

st.title("✅ 자격 확인")
st.write("정보를 입력하시면 받을 수 있는 혜택을 AI가 확인해드립니다.")

# 저장된 프로필 불러오기
saved = load_profile()
if saved:
    st.markdown('<span class="saved-badge">💾 이전에 저장한 정보가 있습니다</span>', unsafe_allow_html=True)
    if st.button("❌ 저장 정보 삭제"):
        delete_profile()
        st.rerun()

st.divider()

CURRENT_YEAR = 2026

with st.form("profile_form"):
    birth_year = st.number_input(
        "태어난 년도 (예: 1955)",
        min_value=1926, max_value=2006,
        value=saved.get("birth_year", 1961),
        step=1,
    )
    age = CURRENT_YEAR - birth_year
    st.caption(f"→ 만 {age}세")
    household = st.selectbox(
        "가구 유형",
        ["단독가구(혼자 사심)", "부부가구", "자녀와 함께 거주", "기타"],
        index=["단독가구(혼자 사심)", "부부가구", "자녀와 함께 거주", "기타"].index(
            saved.get("household", "단독가구(혼자 사심)")
        ),
    )
    income_options = ["월 50만원 미만", "월 50~100만원", "월 100~200만원", "월 200만원 이상"]
    income = st.selectbox(
        "월 소득 수준",
        income_options,
        index=income_options.index(saved.get("income", "월 50~100만원")),
    )
    disability_options = ["없음", "경증장애", "중증장애"]
    disability = st.selectbox(
        "장애 여부",
        disability_options,
        index=disability_options.index(saved.get("disability", "없음")),
    )
    notes = st.text_area("추가 사항 (선택)",
                         value=saved.get("notes", ""),
                         placeholder="예: 만성질환 있음, 혼자 거동 어려움 등")

    col1, col2 = st.columns(2)
    with col1:
        submitted = st.form_submit_button("🔍 자격 확인하기", use_container_width=True)
    with col2:
        save_btn = st.form_submit_button("💾 정보 저장하기", use_container_width=True)

user_profile = {
    "birth_year": birth_year,
    "age": age,
    "household": household,
    "income": income,
    "disability": disability,
    "notes": notes,
}

if save_btn:
    save_profile(user_profile)
    st.success("✅ 정보가 저장되었습니다. 다음에 방문하셔도 자동으로 불러옵니다.")

if submitted:
    save_profile(user_profile)

    st.divider()
    st.subheader("📋 AI 자격 분석 결과")

    benefits = get_benefits_by_age(user_profile["age"])

    for b in benefits:
        with st.expander(f"**{b['name']}**", expanded=True):
            with st.spinner("확인 중..."):
                result = check_eligibility(user_profile, b["name"])
            st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)
