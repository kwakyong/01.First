import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.welfare_api import SAMPLE_BENEFITS
from utils.claude_client import get_application_guide, ask_claude

st.set_page_config(page_title="신청 안내", page_icon="📋", layout="centered")

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

    .guide-card {
        background: white;
        border-radius: 14px;
        padding: 24px 28px;
        color: #1A1A2E;
        font-size: 1rem;
        line-height: 1.9;
        box-shadow: 0 2px 16px rgba(27,42,74,0.07);
        border-top: 4px solid #2C4A8A;
        margin-top: 16px;
    }
    .guide-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1B2A4A;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 2px solid #E8EDF4;
    }

    .chat-section {
        background: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 2px 16px rgba(27,42,74,0.07);
        margin-top: 8px;
    }
    .chat-label {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1B2A4A;
        margin-bottom: 4px;
    }
    .chat-sublabel {
        font-size: 0.9rem;
        color: #7F8C9A;
        margin-bottom: 16px;
    }

    .section-divider {
        font-size: 1.3rem;
        font-weight: 900;
        color: #1B2A4A;
        margin: 32px 0 16px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid #E8EDF4;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <h2>📋 신청 안내</h2>
    <p>원하시는 혜택의 신청 방법을 단계별로 안내해 드립니다</p>
</div>
""", unsafe_allow_html=True)

benefit_names = [b["name"] for b in SAMPLE_BENEFITS]
selected = st.selectbox("혜택 선택", benefit_names, label_visibility="collapsed")

if st.button("📖 신청 방법 알아보기", use_container_width=True, type="primary"):
    with st.spinner("신청 방법을 준비하고 있습니다..."):
        guide = get_application_guide(selected)
    st.markdown(f"""
    <div class="guide-card">
        <div class="guide-title">📌 {selected} 신청 방법</div>
        {guide}
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="section-divider">💬 AI 상담</div>', unsafe_allow_html=True)

st.markdown("""
<div class="chat-section">
    <div class="chat-label">무엇이든 편하게 물어보세요</div>
    <div class="chat-sublabel">복지혜택, 자격 조건, 신청 방법 등 궁금한 점을 질문하세요</div>
</div>
""", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for msg in st.session_state.chat_history:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("예: 기초연금 신청하려면 무엇이 필요한가요?"):
    st.chat_message("user").write(prompt)
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    with st.spinner("답변 작성 중..."):
        response = ask_claude(prompt, st.session_state.chat_history[:-1])

    st.chat_message("assistant").write(response)
    st.session_state.chat_history.append({"role": "assistant", "content": response})
