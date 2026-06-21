import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="자격 확인", page_icon="✅", layout="centered")

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

    .saved-notice {
        background: #E8F5E9; border: 1px solid #A5D6A7; border-radius: 10px;
        padding: 12px 18px; color: #1B5E20; font-size: 0.95rem;
        font-weight: 600; margin-bottom: 16px;
    }
    .form-section-title {
        font-size: 0.85rem; font-weight: 700; color: #2C4A8A;
        letter-spacing: 1.5px; text-transform: uppercase;
        margin: 18px 0 10px 0; padding-bottom: 6px;
        border-bottom: 2px solid #E8EDF4;
    }
    .age-display {
        background: #E8EDF4; border-radius: 10px; padding: 10px 16px;
        color: #1B2A4A; font-weight: 700; font-size: 1rem;
        display: inline-block; margin-top: 6px;
    }
    .result-section-title {
        font-size: 1.2rem; font-weight: 900; color: #1B2A4A;
        margin: 28px 0 16px 0; padding-bottom: 10px;
        border-bottom: 2px solid #E8EDF4;
    }
    .cat-group-title {
        font-size: 1rem; font-weight: 900; color: #1B2A4A;
        margin: 20px 0 6px 0; padding-left: 10px;
        border-left: 4px solid #2C4A8A;
    }
    .result-detail {
        background: #F8F9FB; border-radius: 10px;
        padding: 14px 18px; font-size: 0.95rem;
        color: #2D3748; line-height: 1.8; margin-top: 4px;
    }
    .summary-bar { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
    .summary-chip {
        border-radius: 20px; padding: 6px 16px;
        font-size: 0.88rem; font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

if st.session_state.get("target_group", "senior") == "youth":
    from utils.youth_pages import render_eligibility
else:
    from utils.senior_pages import render_eligibility

render_eligibility()
