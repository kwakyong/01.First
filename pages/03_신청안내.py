import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.welfare_data import WELFARE_BENEFITS
from utils.claude_client import get_application_guide, ask_claude

st.set_page_config(page_title="신청 안내", page_icon="📋", layout="centered")

st.markdown("""
<style>
    .stApp { font-size: 18px; }
    .guide-box {
        background: #eafaf1;
        border-radius: 10px;
        padding: 20px 24px;
        color: #1a2e1a;
        font-size: 1rem;
        line-height: 1.8;
        border: 1px solid #a9dfbf;
    }
</style>
""", unsafe_allow_html=True)

st.title("📋 신청 안내")
st.write("원하시는 혜택을 선택하시면 신청 방법을 안내해드립니다.")
st.divider()

benefit_names = [b["name"] for b in WELFARE_BENEFITS]
selected = st.selectbox("혜택 선택", benefit_names)

if st.button("📖 신청 방법 알아보기", use_container_width=True):
    with st.spinner("신청 방법을 찾고 있습니다..."):
        guide = get_application_guide(selected)
    st.divider()
    st.subheader(f"📌 {selected} 신청 방법")
    st.markdown(f'<div class="guide-box">{guide}</div>', unsafe_allow_html=True)

st.divider()
st.subheader("💬 AI 상담")
st.write("궁금하신 점을 편하게 물어보세요.")

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
