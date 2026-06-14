import streamlit as st

st.set_page_config(
    page_title="내 복지 찾기",
    page_icon="🏛️",
    layout="centered",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
    }

    .hero {
        background: linear-gradient(135deg, #1B2A4A 0%, #2C4A8A 100%);
        border-radius: 20px;
        padding: 52px 32px 44px 32px;
        text-align: center;
        color: white;
        margin-bottom: 36px;
        box-shadow: 0 8px 32px rgba(27, 42, 74, 0.25);
    }
    .hero-title {
        font-size: 2.4rem;
        font-weight: 900;
        letter-spacing: -0.5px;
        margin-bottom: 12px;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        color: #B8CCE8;
        font-weight: 400;
        line-height: 1.7;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(255,255,255,0.15);
        color: #E8F0FC;
        border-radius: 20px;
        padding: 5px 16px;
        font-size: 0.85rem;
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.2);
        letter-spacing: 1px;
    }

    .feature-card {
        background: white;
        border-radius: 16px;
        padding: 32px 20px 28px 20px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(27, 42, 74, 0.08);
        border-top: 4px solid #2C4A8A;
        height: 100%;
    }
    .feature-icon {
        font-size: 2.4rem;
        margin-bottom: 14px;
    }
    .feature-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1B2A4A;
        margin-bottom: 8px;
    }
    .feature-desc {
        font-size: 0.9rem;
        color: #7F8C9A;
        line-height: 1.6;
    }

    .info-bar {
        background: #E8EDF4;
        border-radius: 12px;
        padding: 16px 24px;
        margin-top: 28px;
        border-left: 4px solid #2C4A8A;
        color: #1B2A4A;
        font-size: 1rem;
    }

    .section-label {
        font-size: 0.8rem;
        font-weight: 700;
        color: #7F8C9A;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 20px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <div class="hero-badge">🏛️ 복지 정보 서비스</div>
    <div class="hero-title">내 복지 찾기</div>
    <div class="hero-subtitle">
        국가·지역 복지혜택을 한눈에 확인하고<br>
        내가 받을 수 있는 혜택을 AI가 안내해드립니다
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-label">주요 서비스</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🔍</div>
        <div class="feature-title">혜택 조회</div>
        <div class="feature-desc">국가·지역 복지혜택<br>전체 목록 확인</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">✅</div>
        <div class="feature-title">자격 확인</div>
        <div class="feature-desc">내 정보 입력 후<br>AI 자격 분석</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📋</div>
        <div class="feature-title">신청 안내</div>
        <div class="feature-desc">단계별 신청 방법과<br>AI 상담 서비스</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="info-bar">
    👈 왼쪽 메뉴에서 원하시는 서비스를 선택하세요
</div>
""", unsafe_allow_html=True)
