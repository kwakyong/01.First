import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.welfare_api import TOP_BENEFITS, TOP_TO_USER_CAT
from utils.claude_client import get_application_guide, ask_claude
from utils.profile_manager import (
    load_profile, load_eligibility_results,
    load_bookmarks, save_bookmark, remove_bookmark,
)

st.set_page_config(page_title="신청 안내", page_icon="📋", layout="centered")

CAT_ICON = {
    "노후·연금": "💛", "의료·건강": "🏥", "돌봄·요양": "🤝",
    "생활지원": "🛒", "일자리·창업": "💼", "주거": "🏠",
    "장애지원": "♿", "안전·긴급": "🚨", "여가·문화": "🎭", "기타": "📌",
}

BOOKMARK_OPTS = ["관심", "신청예정", "완료"]
BOOKMARK_ICON = {"관심": "⭐", "신청예정": "📌", "완료": "✔️"}

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

st.markdown("""
<div class="page-header">
    <h2>📋 신청 안내</h2>
    <p>자격 확인된 혜택의 신청 방법을 단계별로 안내해 드립니다</p>
</div>
""", unsafe_allow_html=True)

# ─── 데이터 로드 ────────────────────────────────────────
eligibility  = load_eligibility_results()   # {서비스명: {status, reason}}
user_profile = load_profile()
bookmarks    = load_bookmarks()             # {서비스명: "관심"|"신청예정"|"완료"}

# ─── 혜택 목록 구성 ────────────────────────────────────
possible_names  = [b["name"] for b in TOP_BENEFITS
                   if eligibility.get(b["name"], {}).get("status") == "가능"]
check_names     = [b["name"] for b in TOP_BENEFITS
                   if eligibility.get(b["name"], {}).get("status") == "확인필요"]
all_names       = [b["name"] for b in TOP_BENEFITS]

# 보기 모드 선택
if eligibility:
    st.markdown(
        f'<div class="info-banner">✅ 자격확인 결과: <b>가능 {len(possible_names)}개</b>, '
        f'확인필요 {len(check_names)}개 — 가능 혜택을 우선 표시합니다</div>',
        unsafe_allow_html=True
    )
    view_mode = st.radio(
        "표시 범위",
        ["✅ 가능 혜택만", "⚠️ 확인필요 포함", "📋 전체 목록"],
        horizontal=True, label_visibility="collapsed"
    )
    if view_mode == "✅ 가능 혜택만":
        display_names = possible_names if possible_names else all_names
    elif view_mode == "⚠️ 확인필요 포함":
        display_names = possible_names + check_names
    else:
        display_names = all_names
else:
    st.markdown(
        '<div class="warn-banner">⚠️ 자격확인을 먼저 실행하시면 가능한 혜택만 볼 수 있습니다</div>',
        unsafe_allow_html=True
    )
    display_names = all_names

if not display_names:
    display_names = all_names

# ─── 혜택 선택 ─────────────────────────────────────────
benefit_map = {b["name"]: b for b in TOP_BENEFITS}

st.markdown(
    '<div style="font-size:1rem;font-weight:700;color:#1B2A4A;margin-bottom:6px;">'
    '👇 아래 목록에서 신청할 혜택을 선택하신 후 <span style="color:#2C4A8A;">📖 신청 방법 알아보기</span> 버튼을 눌러주세요'
    '</div>',
    unsafe_allow_html=True
)

def _label(name: str) -> str:
    res = eligibility.get(name, {})
    status = res.get("status", "")
    bm = bookmarks.get(name, "")
    icons = ""
    if status == "가능":      icons += "✅ "
    elif status == "확인필요": icons += "⚠️ "
    if bm:                    icons += BOOKMARK_ICON.get(bm, "") + " "
    return icons + name

labeled = [_label(n) for n in display_names]
selected_label = st.selectbox("혜택 선택", labeled, label_visibility="collapsed")
selected = display_names[labeled.index(selected_label)]
benefit  = benefit_map.get(selected, {})

# 선택된 혜택 정보 요약
res = eligibility.get(selected, {})
status = res.get("status", "")
reason = res.get("reason", "")
user_cat = TOP_TO_USER_CAT.get(benefit.get("category", ""), "기타")
cat_icon = CAT_ICON.get(user_cat, "📌")

if status:
    sty = {"가능": ("chip-possible","✅"), "확인필요": ("chip-check","⚠️"), "불가": ("","❌")}.get(status, ("chip-all",""))
    st.markdown(
        f'<span class="benefit-chip {sty[0]}">{sty[1]} {status}</span>'
        f'<span class="benefit-chip chip-all">{cat_icon} {user_cat}</span>'
        + (f'　<span style="font-size:0.88rem;color:#7F8C9A;">{reason}</span>' if reason else ""),
        unsafe_allow_html=True
    )

# ─── 신청 방법 안내 ─────────────────────────────────────
if st.button("📖 신청 방법 알아보기", use_container_width=True, type="primary"):
    with st.spinner("신청 방법을 준비하고 있습니다..."):
        guide = get_application_guide(selected, user_profile if user_profile else None)
    st.markdown(f"""
    <div class="guide-card">
        <div class="guide-title">📌 {selected} 신청 방법</div>
        {guide}
    </div>
    """, unsafe_allow_html=True)

# ─── 신청 진행 상태 ────────────────────────────────────
st.divider()

bm_current = bookmarks.get(selected, "")
st.markdown(
    '<div class="status-card-title">📌 신청 진행 상태 기록</div>',
    unsafe_allow_html=True
)
st.markdown(
    '위에서 선택한 신청가능 혜택의 상태를 지정하고 <b>상태 저장</b>을 누르세요.',
    unsafe_allow_html=True
)

bm_col1, bm_col2 = st.columns([3, 1])
with bm_col1:
    bm_select = st.selectbox(
        "신청 진행 상태",
        ["기록 안 함", "⭐ 관심 (더 알아볼 예정)", "📌 신청예정 (곧 신청할 것)", "✔️ 완료 (이미 신청함)"],
        index=(BOOKMARK_OPTS.index(bm_current) + 1) if bm_current in BOOKMARK_OPTS else 0,
        label_visibility="collapsed",
        help="선택 후 '상태 저장' 버튼을 누르세요"
    )
with bm_col2:
    st.write("")  # 버튼 위치 맞춤
    if st.button("상태 저장", use_container_width=True):
        if bm_select == "기록 안 함":
            remove_bookmark(selected)
            st.toast("기록이 삭제되었습니다.")
        else:
            label_map = {
                "⭐ 관심 (더 알아볼 예정)": "관심",
                "📌 신청예정 (곧 신청할 것)": "신청예정",
                "✔️ 완료 (이미 신청함)": "완료",
            }
            save_bookmark(selected, label_map[bm_select])
            st.toast(f"'{selected}' 상태가 저장되었습니다.")
        st.rerun()

if bm_current:
    st.markdown(
        f'<div class="bm-row">{BOOKMARK_ICON.get(bm_current,"")} 현재 기록: <b>{bm_current}</b>　'
        f'<span style="color:#B0B8C1;">위에서 다시 선택하여 변경하거나 삭제할 수 있습니다</span></div>',
        unsafe_allow_html=True
    )

# ─── 북마크 현황 요약 ───────────────────────────────────
if bookmarks:
    st.markdown('<div class="section-divider">📋 내 신청 진행 현황</div>', unsafe_allow_html=True)
    st.caption("혜택별로 기록해 둔 신청 진행 상태입니다. 위에서 혜택을 선택해 상태를 변경할 수 있습니다.")
    for bm_status in BOOKMARK_OPTS:
        names_in = [n for n, s in bookmarks.items() if s == bm_status]
        if names_in:
            icon = BOOKMARK_ICON.get(bm_status, "")
            desc = {"관심": "더 알아볼 예정", "신청예정": "곧 신청할 것", "완료": "이미 신청함"}.get(bm_status, "")
            st.markdown(
                f"**{icon} {bm_status}** ({desc}) — {len(names_in)}개: "
                + " · ".join(names_in)
            )

# ─── AI 상담 ────────────────────────────────────────────
st.markdown('<div class="section-divider">💬 AI 상담</div>', unsafe_allow_html=True)
st.caption("복지혜택, 자격 조건, 신청 방법 등 궁금한 점을 질문하세요")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for msg in st.session_state.chat_history:
    st.chat_message(msg["role"]).write(msg["content"])

placeholder = f"예: '{selected}' 신청 시 필요한 서류가 뭔가요?"
if prompt := st.chat_input(placeholder):
    st.chat_message("user").write(prompt)
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    context = f"현재 '{selected}' 혜택의 신청 방법을 알아보는 중입니다. " if selected else ""
    with st.spinner("답변 작성 중..."):
        response = ask_claude(context + prompt, st.session_state.chat_history[:-1])

    st.chat_message("assistant").write(response)
    st.session_state.chat_history.append({"role": "assistant", "content": response})
