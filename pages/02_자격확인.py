import streamlit as st
import sys
import os
from collections import defaultdict
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.welfare_api import TOP_BENEFITS, TOP_TO_USER_CAT
from utils.claude_client import check_all_eligibility
from utils.profile_manager import save_profile, load_profile, delete_profile, save_eligibility_results

st.set_page_config(page_title="자격 확인", page_icon="✅", layout="centered")

CURRENT_YEAR = 2026

STATUS_STYLE = {
    "가능":    {"bg": "#E8F5E9", "color": "#1B5E20", "border": "#A5D6A7", "icon": "✅"},
    "불가":    {"bg": "#FFEBEE", "color": "#B71C1C", "border": "#EF9A9A", "icon": "❌"},
    "확인필요": {"bg": "#FFF8E1", "color": "#7D6608", "border": "#FFE082", "icon": "⚠️"},
}

CAT_ICON = {
    "노후·연금": "💛", "의료·건강": "🏥", "돌봄·요양": "🤝",
    "생활지원": "🛒", "일자리·창업": "💼", "주거": "🏠",
    "장애지원": "♿", "안전·긴급": "🚨", "여가·문화": "🎭", "기타": "📌",
}

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

# ─── 입력 폼 ───────────────────────────────────────────
with st.form("profile_form"):

    # 섹션 1: 기본 정보
    st.markdown('<div class="form-section-title">👤 기본 정보</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        birth_year = st.number_input(
            "태어난 년도", min_value=1926, max_value=2006,
            value=saved.get("birth_year", 1961), step=1,
            help="주민등록상 출생년도"
        )
        age = CURRENT_YEAR - birth_year
        st.markdown(f'<div class="age-display">만 {age}세</div>', unsafe_allow_html=True)
    with col2:
        gender_opts = ["남성", "여성"]
        gender = st.selectbox("성별", gender_opts,
            index=gender_opts.index(saved.get("gender", "남성")))

    # 섹션 2: 가구 현황
    st.markdown('<div class="form-section-title">🏠 가구 현황</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        household_opts = ["단독가구(혼자 사심)", "부부가구", "자녀와 함께 거주", "기타"]
        household = st.selectbox("가구 유형", household_opts,
            index=household_opts.index(saved.get("household", "단독가구(혼자 사심)")))
    with col2:
        size_opts = ["1인", "2인", "3인", "4인 이상"]
        household_size = st.selectbox("가구원 수", size_opts,
            index=size_opts.index(saved.get("household_size", "1인")))

    col1, col2 = st.columns(2)
    with col1:
        own_biz_opts = ["없음", "있음"]
        own_business = st.selectbox("본인 사업자등록 여부", own_biz_opts,
            index=own_biz_opts.index(saved.get("own_business", "없음")))
    with col2:
        spouse_biz_opts = ["해당없음(배우자 없음)", "없음", "있음"]
        saved_spouse = saved.get("spouse_business", "해당없음(배우자 없음)")
        if saved_spouse not in spouse_biz_opts:
            saved_spouse = "해당없음(배우자 없음)"
        spouse_business = st.selectbox("배우자 사업자등록 여부", spouse_biz_opts,
            index=spouse_biz_opts.index(saved_spouse))

    # 섹션 3: 소득·재산
    st.markdown('<div class="form-section-title">💰 소득·재산</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        income_opts = ["월 50만원 미만", "월 50~100만원", "월 100~200만원", "월 200만원 이상"]
        income = st.selectbox("월 소득 수준 (가구 합산)", income_opts,
            index=income_opts.index(saved.get("income", "월 50~100만원")))
    with col2:
        home_opts = ["자가(본인 소유)", "전세", "월세·보증금", "무주택(무료 거주 등)"]
        saved_home = saved.get("home_ownership", "자가(본인 소유)")
        if saved_home not in home_opts:
            saved_home = "자가(본인 소유)"
        home_ownership = st.selectbox("주택 소유 현황", home_opts,
            index=home_opts.index(saved_home))

    asset_opts = ["1억 미만", "1억~3억", "3억~5억", "5억 이상"]
    saved_asset = saved.get("asset_level", "1억 미만")
    if saved_asset not in asset_opts:
        saved_asset = "1억 미만"
    asset_level = st.selectbox("재산 규모 (부동산+금융자산 합산)", asset_opts,
        index=asset_opts.index(saved_asset))

    # 섹션 4: 건강·장애
    st.markdown('<div class="form-section-title">🏥 건강·장애</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        disability_opts = ["없음", "경증장애", "중증장애"]
        disability = st.selectbox("장애 여부", disability_opts,
            index=disability_opts.index(saved.get("disability", "없음")))
    with col2:
        health_opts = ["특이사항 없음", "만성질환(고혈압·당뇨 등)", "치매 진단", "거동 불편(와상·이동 어려움)"]
        saved_health = saved.get("health_condition", "특이사항 없음")
        if saved_health not in health_opts:
            saved_health = "특이사항 없음"
        health_condition = st.selectbox("주요 건강 상태", health_opts,
            index=health_opts.index(saved_health))

    # 섹션 5: 기타
    st.markdown('<div class="form-section-title">📋 기타</div>', unsafe_allow_html=True)
    veteran_opts = ["없음", "국가유공자", "참전유공자"]
    saved_veteran = saved.get("veteran", "없음")
    if saved_veteran not in veteran_opts:
        saved_veteran = "없음"
    veteran = st.selectbox("국가·참전유공자 여부", veteran_opts,
        index=veteran_opts.index(saved_veteran))

    notes = st.text_area("추가 사항 (선택)", value=saved.get("notes", ""),
        placeholder="예: 기초생활수급자, 의료급여 대상자, 독거노인 등")

    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        submitted = st.form_submit_button("🔍 자격 확인하기", use_container_width=True, type="primary")
    with col2:
        save_btn = st.form_submit_button("💾 정보 저장하기", use_container_width=True)

# ─── 프로필 구성 ───────────────────────────────────────
user_profile = {
    "birth_year": birth_year, "age": age, "gender": gender,
    "household": household, "household_size": household_size,
    "income": income, "home_ownership": home_ownership, "asset_level": asset_level,
    "disability": disability, "health_condition": health_condition,
    "own_business": own_business, "spouse_business": spouse_business,
    "veteran": veteran, "notes": notes,
}

if save_btn:
    save_profile(user_profile)
    st.success("✅ 정보가 저장되었습니다. 다음 방문 시 자동으로 불러옵니다.")

# ─── AI 자격 분석 결과 ─────────────────────────────────
if submitted:
    save_profile(user_profile)
    st.markdown('<div class="result-section-title">📊 AI 자격 분석 결과</div>', unsafe_allow_html=True)

    with st.spinner("AI가 40개 복지서비스를 한 번에 분석하는 중입니다... (약 20~30초 소요)"):
        results = check_all_eligibility(user_profile, TOP_BENEFITS)

    save_eligibility_results(results)

    # 요약 카운트
    cnt = {"가능": 0, "불가": 0, "확인필요": 0}
    for v in results.values():
        s = v.get("status", "확인필요")
        if s in cnt:
            cnt[s] += 1

    col_s1, col_s2, col_s3, col_s4 = st.columns([2, 2, 2, 3])
    with col_s1:
        st.markdown(f'<div class="summary-chip" style="background:#E8F5E9;color:#1B5E20;border:1px solid #A5D6A7;">✅ 가능 {cnt["가능"]}개</div>', unsafe_allow_html=True)
    with col_s2:
        st.markdown(f'<div class="summary-chip" style="background:#FFF8E1;color:#7D6608;border:1px solid #FFE082;">⚠️ 확인필요 {cnt["확인필요"]}개</div>', unsafe_allow_html=True)
    with col_s3:
        st.markdown(f'<div class="summary-chip" style="background:#FFEBEE;color:#B71C1C;border:1px solid #EF9A9A;">❌ 불가 {cnt["불가"]}개</div>', unsafe_allow_html=True)
    with col_s4:
        st.page_link("pages/03_신청안내.py", label="📋 가능 혜택 신청안내 보기 →", use_container_width=True)

    # 카테고리별 그룹화
    grouped = defaultdict(list)
    for b in TOP_BENEFITS:
        user_cat = TOP_TO_USER_CAT.get(b["category"], "기타")
        grouped[user_cat].append(b)

    # 가능 항목이 있는 카테고리를 먼저
    def cat_sort_key(cat):
        has_possible = any(results.get(b["name"], {}).get("status") == "가능"
                           for b in grouped[cat])
        return (0 if has_possible else 1, cat)

    for user_cat in sorted(grouped.keys(), key=cat_sort_key):
        icon = CAT_ICON.get(user_cat, "📌")
        st.markdown(f'<div class="cat-group-title">{icon} {user_cat}</div>', unsafe_allow_html=True)

        for b in grouped[user_cat]:
            res = results.get(b["name"], {"status": "확인필요", "reason": "결과 없음"})
            status = res.get("status", "확인필요")
            reason = res.get("reason", "")
            sty = STATUS_STYLE.get(status, STATUS_STYLE["확인필요"])

            with st.expander(f"{sty['icon']} {b['name']}  —  {status}", expanded=False):
                st.markdown(f"""
                <div class="result-detail">
                    <b style="color:{sty['color']};">{sty['icon']} {status}</b> &nbsp; {reason}
                    <br><br>
                    <span style="color:#4A5568;font-size:0.9rem;">{b['description']}</span>
                </div>
                """, unsafe_allow_html=True)
                st.caption(f"📍 신청: {b['apply_where']}  ·  대상: {b['age_min']}세 이상, {b['income_level']}")
