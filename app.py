import streamlit as st

APP_VERSION = "2.1"

# set_page_config는 st.navigation() 보다 먼저 호출
st.set_page_config(
    page_title="내 복지 찾기",
    page_icon="🏛️",
    layout="centered",
)

# 그룹 초기화 — navigation() 호출 전에 확정해야 타이틀에 반영됨
if "target_group" not in st.session_state:
    st.session_state["target_group"] = "senior"

_group = st.session_state["target_group"]
if _group == "senior":
    _home_title = "app (어르신 복지 60세이상)"
else:
    _home_title = "app (청소년·대학생 복지)"


def _home():
    st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }

    .hero {
        background: linear-gradient(135deg, #1B2A4A 0%, #2C4A8A 100%);
        border-radius: 20px; padding: 52px 32px 44px 32px;
        text-align: center; color: white; margin-bottom: 36px;
        box-shadow: 0 8px 32px rgba(27, 42, 74, 0.25);
    }
    .hero-title { font-size: 2.4rem; font-weight: 900; letter-spacing: -0.5px; margin-bottom: 12px; }
    .hero-subtitle { font-size: 1.1rem; color: #B8CCE8; font-weight: 400; line-height: 1.7; }
    .hero-badge {
        display: inline-block; background: rgba(255,255,255,0.15); color: #E8F0FC;
        border-radius: 20px; padding: 5px 16px; font-size: 0.85rem;
        margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.2); letter-spacing: 1px;
    }
    .feature-card {
        background: white; border-radius: 16px; padding: 32px 20px 28px 20px;
        text-align: center; box-shadow: 0 4px 20px rgba(27, 42, 74, 0.08);
        border-top: 4px solid #2C4A8A; height: 100%;
    }
    .feature-icon { font-size: 2.4rem; margin-bottom: 14px; }
    .feature-title { font-size: 1.15rem; font-weight: 700; color: #1B2A4A; margin-bottom: 8px; }
    .feature-desc  { font-size: 0.9rem; color: #7F8C9A; line-height: 1.6; }
    .info-bar {
        background: #E8EDF4; border-radius: 12px; padding: 16px 24px;
        margin-top: 28px; border-left: 4px solid #2C4A8A; color: #1B2A4A; font-size: 1rem;
    }
    .section-label {
        font-size: 0.8rem; font-weight: 700; color: #7F8C9A;
        letter-spacing: 2px; text-transform: uppercase; margin-bottom: 20px; text-align: center;
    }
    .group-select-label { font-size: 0.9rem; font-weight: 700; color: #1B2A4A; text-align: center; margin-bottom: 12px; }
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

    st.markdown('<div class="group-select-label">👇 나에게 맞는 복지 유형을 선택하세요</div>', unsafe_allow_html=True)
    g_col1, g_col2 = st.columns(2, gap="medium")
    with g_col1:
        if st.button("🧓 어르신 복지\n(60세 이상)", use_container_width=True,
                     type="primary" if st.session_state["target_group"] == "senior" else "secondary"):
            st.session_state["target_group"] = "senior"
            st.rerun()
    with g_col2:
        if st.button("🎓 청소년·대학생 복지\n(만 15~24세)", use_container_width=True,
                     type="primary" if st.session_state["target_group"] == "youth" else "secondary"):
            st.session_state["target_group"] = "youth"
            st.rerun()

    group_label = "어르신 복지" if st.session_state["target_group"] == "senior" else "청소년·대학생 복지"
    st.markdown(f"""
<div class="info-bar">
    ✅ <b>{group_label}</b> 모드로 설정되었습니다<br>
    <span style="font-size:0.9rem;font-weight:400;">👈 왼쪽 상단 &gt;&gt; 를 선택하여 서비스를 선택하세요.</span>
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-label">주요 서비스</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3, gap="medium")
    with col1:
        st.markdown("""
<div class="feature-card">
    <div class="feature-icon">🔍</div>
    <div class="feature-title">혜택 조회</div>
    <div class="feature-desc">국가·지역 복지혜택<br>전체 목록 확인</div>
</div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
<div class="feature-card">
    <div class="feature-icon">✅</div>
    <div class="feature-title">자격 확인</div>
    <div class="feature-desc">내 정보 입력 후<br>AI 자격 분석</div>
</div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""
<div class="feature-card">
    <div class="feature-icon">📋</div>
    <div class="feature-title">신청 안내</div>
    <div class="feature-desc">단계별 신청 방법과<br>AI 상담 서비스</div>
</div>""", unsafe_allow_html=True)


# ── 네비게이션 정의 ─────────────────────────────────────────────────────────
pg = st.navigation([
    st.Page(_home, title=_home_title, icon="🏛️", default=True),
    st.Page("pages/01_혜택조회.py", title="혜택조회", icon="🔍"),
    st.Page("pages/02_자격확인.py", title="자격확인", icon="✅"),
    st.Page("pages/03_신청안내.py", title="신청안내", icon="📋"),
])

with st.sidebar:
    st.markdown("---")
    st.markdown(
        f'<div style="text-align:center;font-size:0.75rem;color:#9FA6B2;padding:4px 0;">'
        f'내 복지 찾기 &nbsp;v{APP_VERSION}</div>',
        unsafe_allow_html=True,
    )

pg.run()
