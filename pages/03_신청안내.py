import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="신청 안내", page_icon="📋", layout="centered")

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

    .info-banner {
        background: #E8F5E9; border: 1px solid #A5D6A7; border-radius: 12px;
        padding: 14px 20px; color: #1B5E20; font-size: 0.95rem;
        font-weight: 600; margin-bottom: 16px;
    }
    .warn-banner {
        background: #FFF8E1; border: 1px solid #FFE082; border-radius: 12px;
        padding: 14px 20px; color: #7D6608; font-size: 0.95rem;
        font-weight: 600; margin-bottom: 16px;
    }
    .benefit-chip {
        display: inline-block; border-radius: 20px; padding: 4px 12px;
        font-size: 0.8rem; font-weight: 700; margin: 2px;
    }
    .chip-possible  { background: #E8F5E9; color: #1B5E20; border: 1px solid #A5D6A7; }
    .chip-check     { background: #FFF8E1; color: #7D6608; border: 1px solid #FFE082; }
    .chip-all       { background: #E8EDF4; color: #1B2A4A; border: 1px solid #B8CCE8; }
    .guide-card {
        background: white; border-radius: 14px; padding: 26px 28px;
        color: #1A1A2E; font-size: 0.97rem; line-height: 1.9;
        box-shadow: 0 2px 16px rgba(27,42,74,0.07);
        border-top: 4px solid #2C4A8A; margin-top: 16px;
    }
    .guide-title {
        font-size: 1.15rem; font-weight: 700; color: #1B2A4A;
        margin-bottom: 14px; padding-bottom: 10px;
        border-bottom: 2px solid #E8EDF4;
    }
    .section-divider {
        font-size: 1.15rem; font-weight: 900; color: #1B2A4A;
        margin: 32px 0 14px 0; padding-bottom: 8px;
        border-bottom: 2px solid #E8EDF4;
    }
    .bm-row { font-size: 0.85rem; color: #7F8C9A; margin-top: 8px; }
    .status-card {
        background: #F0F4FF; border: 1.5px solid #B8CCE8; border-radius: 12px;
        padding: 16px 20px; margin: 16px 0 8px 0;
    }
    .status-card-title {
        font-size: 0.9rem; font-weight: 700; color: #2C4A8A;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

if st.session_state.get("target_group", "senior") == "youth":
    from utils.youth_pages import render_guide
else:
    from utils.senior_pages import render_guide

render_guide()
