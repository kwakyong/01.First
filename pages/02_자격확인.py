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

    .saved-notice {
        background: #E8F5E9;
        border: 1px solid #A5D6A7;
        border-radius: 10px;
        padding: 12px 18px;
        color: #1B5E20;
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .form-section {
        background: white;
        border-radius: 16px;
        padding: 28px;
        box-shadow: 0 2px 16px rgba(27,42,74,0.07);
        margin-bottom: 20px;
    }
    .result-card {
        background: white;
        border-radius: 12px;
        padding: 20px 24px;
        color: #1A1A2E;
        font-size: 1rem;
        line-height: 1.8;
        border-left: 5px solid #2C4A8A;
        box-shadow: 0 2px 12px rgba(27,42,74,0.07);
    }
    .result-section-title {
        font-size: 1.3rem;
        font-weight: 900;
        color: #1B2A4A;
        margin: 28px 0 16px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid #E8EDF4;
    }
    .age-display {
        background: #E8EDF4;
        border-radius: 10px;
        padding: 10px 16px;
        color: #1B2A4A;
        font-weight: 700;
        font-size: 1rem;
        margin-top: 6px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <h2>✅ 자격 확인</h2>
    <p>내 정보를 입력하시면 AI가 받을 수 있는 혜택을 분석해 드립니다</p>
</div>
""", unsafe_allow_html=True)

saved = load_profile()
if saved:
    st.markdown('<div class="saved-notice">💾 이전에 저장한 정보가 있습니다</div>', unsafe_allow_html=True)
    if st.button("❌ 저장 정보 삭제"):
        delete_profile()
        st.rerun()

CURRENT_YEAR = 2026

st.markdown('<div class="form-section">', unsafe_allow_html=True)
with st.form("profile_form"):
    birth_year = st.number_input(
        "태어난 년도",
        min_value=1926, max_value=2006,
        value=saved.get("birth_year", 1961),
        step=1,
        help="주민등록상 출생년도를 입력하세요"
    )
    age = CURRENT_YEAR - birth_year
    st.markdown(f'<div class="age-display">만 {age}세</div>', unsafe_allow_html=True)

    st.write("")
    household_options = ["단독가구(혼자 사심)", "부부가구", "자녀와 함께 거주", "기타"]
    household = st.selectbox("가구 유형", household_options,
        index=household_options.index(saved.get("household", "단독가구(혼자 사심)")))

    income_options = ["월 50만원 미만", "월 50~100만원", "월 100~200만원", "월 200만원 이상"]
    income = st.selectbox("월 소득 수준", income_options,
        index=income_options.index(saved.get("income", "월 50~100만원")))

    disability_options = ["없음", "경증장애", "중증장애"]
    disability = st.selectbox("장애 여부", disability_options,
        index=disability_options.index(saved.get("disability", "없음")))

    notes = st.text_area("추가 사항 (선택)", value=saved.get("notes", ""),
        placeholder="예: 만성질환 있음, 혼자 거동 어려움 등")

    col1, col2 = st.columns(2)
    with col1:
        submitted = st.form_submit_button("🔍 자격 확인하기", use_container_width=True, type="primary")
    with col2:
        save_btn = st.form_submit_button("💾 정보 저장하기", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

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
    st.success("✅ 정보가 저장되었습니다. 다음 방문 시 자동으로 불러옵니다.")

if submitted:
    save_profile(user_profile)
    st.markdown('<div class="result-section-title">📋 AI 자격 분석 결과</div>', unsafe_allow_html=True)

    benefits = get_benefits_by_age(user_profile["age"])
    for b in benefits:
        with st.expander(f"**{b['name']}**", expanded=True):
            with st.spinner("분석 중..."):
                result = check_eligibility(user_profile, b["name"])
            st.markdown(f'<div class="result-card">{result}</div>', unsafe_allow_html=True)
