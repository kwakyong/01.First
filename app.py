import streamlit as st

st.set_page_config(
    page_title="내 복지 찾기",
    page_icon="🏠",
    layout="centered",
)

st.markdown("""
<style>
    .big-title {
        font-size: 2.2rem;
        font-weight: bold;
        color: #1a5276;
        text-align: center;
        padding: 20px 0 8px 0;
    }
    .subtitle {
        font-size: 1.15rem;
        color: #34495e;
        text-align: center;
        margin-bottom: 28px;
    }
    .menu-card {
        background: #eaf4fb;
        border-radius: 16px;
        padding: 24px 16px;
        text-align: center;
        font-size: 1.1rem;
        color: #1a5276;
        border: 2px solid #aed6f1;
        line-height: 1.8;
    }
    .stApp { font-size: 18px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">🏠 내 복지 찾기</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">국가·지역 복지혜택을 쉽게 찾아드립니다</div>', unsafe_allow_html=True)

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="menu-card">🔍<br><b>혜택 조회</b><br><small>복지혜택 목록 보기</small></div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="menu-card">✅<br><b>자격 확인</b><br><small>내가 받을 수 있는지 확인</small></div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="menu-card">📋<br><b>신청 안내</b><br><small>신청 방법 알아보기</small></div>', unsafe_allow_html=True)

st.divider()
st.info("👈 왼쪽 메뉴에서 원하는 기능을 선택하세요.", icon="ℹ️")
