import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="혜택 조회", page_icon="🔍", layout="centered")

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

if st.session_state.get("target_group", "senior") == "youth":
    from utils.youth_pages import render_benefits
else:
    from utils.senior_pages import render_benefits

render_benefits()
