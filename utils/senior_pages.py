"""어르신 복지 전용 렌더링 모듈 — 혜택조회 / 자격확인 / 신청안내"""
import streamlit as st
from collections import defaultdict

from utils.welfare_api import TOP_BENEFITS, USER_CATEGORIES, TOP_TO_USER_CAT, REGIONS, get_benefits_by_region
from utils.claude_client import check_all_eligibility, get_application_guide, ask_claude
from utils.profile_manager import (
    save_profile, load_profile, delete_profile, save_eligibility_results,
    load_eligibility_results, load_bookmarks, save_bookmark, remove_bookmark,
)

MINISTRY_ICON = {
    "보건복지부": "🏥", "고용노동부": "💼", "행정안전부": "🏛️",
    "국토교통부": "🏠", "여성가족부": "👨‍👩‍👧", "교육부": "📚",
    "문화체육관광부": "🎭", "국가보훈처": "🎖️", "국가보훈부": "🎖️",
    "기획재정부": "💰", "환경부": "🌿", "농림축산식품부": "🌾",
    "중소벤처기업부": "🏢",
}

CAT_ICON = {
    "노후·연금": "💛", "의료·건강": "🏥", "돌봄·요양": "🤝",
    "생활지원": "🛒", "일자리·창업": "💼", "주거": "🏠",
    "장애지원": "♿", "안전·긴급": "🚨", "여가·문화": "🎭", "기타": "📌",
}

BOOKMARK_OPTS = ["관심", "신청예정", "완료"]
BOOKMARK_ICON = {"관심": "⭐", "신청예정": "📌", "완료": "✔️"}

STATUS_STYLE = {
    "가능":    {"color": "#1B5E20", "icon": "✅"},
    "불가":    {"color": "#B71C1C", "icon": "❌"},
    "확인필요": {"color": "#7D6608", "icon": "⚠️"},
}

CURRENT_YEAR = 2026


@st.cache_data(ttl=3600)
def _load_senior_benefits(region: str):
    return get_benefits_by_region(region)


# ── 혜택 조회 ──────────────────────────────────────────────────────────────
def render_benefits():
    st.markdown("""
    <div class="page-header">
        <h2>🔍 복지혜택 조회</h2>
        <p>국가와 지역에서 제공하는 복지혜택 전체 목록입니다</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        selected_region = st.selectbox("🗺️ 지역 선택", REGIONS, index=0)
    with col2:
        cat_options = ["전체"] + USER_CATEGORIES
        selected_cat = st.selectbox("📂 분야 선택", cat_options, index=0)

    search_query = st.text_input(
        "검색", placeholder="🔍  서비스명 또는 내용으로 검색하세요  예) 의료비, 식사, 연금",
        label_visibility="collapsed"
    )

    all_api_benefits, debug_msg = _load_senior_benefits(selected_region)
    st.caption(debug_msg)
    st.divider()

    # 추천 서비스
    top_filtered = [b for b in TOP_BENEFITS
                    if (selected_cat == "전체" or TOP_TO_USER_CAT.get(b["category"]) == selected_cat)
                    and (not search_query or search_query.lower() in b["name"].lower()
                         or search_query.lower() in b.get("description", "").lower())]

    if top_filtered:
        st.markdown('<div class="section-title">⭐ 추천 서비스</div>', unsafe_allow_html=True)
        for b in top_filtered:
            user_cat = TOP_TO_USER_CAT.get(b["category"], "기타")
            cat_icon = CAT_ICON.get(user_cat, "📌")
            st.markdown(f"""
            <div class="top-card">
                <div class="benefit-title">{b['name']}</div>
                <div class="benefit-desc">{b['description']}</div>
                <div class="tags">
                    <span class="tag tag-top">⭐ 추천</span>
                    <span class="tag tag-cat">{cat_icon} {user_cat}</span>
                    <span class="tag tag-amount">💰 {b['amount']}</span>
                    <span class="tag tag-target">👤 {b['age_min']}세 이상 · {b['income_level']}</span>
                    <span class="tag tag-region">🗺️ 전국공통</span>
                </div>
                <div class="apply-row">📍 {b['apply_where']}</div>
            </div>
            """, unsafe_allow_html=True)

    # 전체 API 서비스
    st.markdown('<div class="section-title">📋 전체 서비스 목록</div>', unsafe_allow_html=True)
    api_benefits = all_api_benefits
    if selected_cat != "전체":
        api_benefits = [b for b in api_benefits if b.get("user_category") == selected_cat]
    if search_query:
        q = search_query.lower()
        api_benefits = [b for b in api_benefits
                        if q in b["name"].lower() or q in b.get("description", "").lower()]

    grouped = defaultdict(list)
    for b in api_benefits:
        grouped[b["category"]].append(b)

    st.markdown(
        f'<div class="count-badge">총 {len(api_benefits)}개 서비스 · {len(grouped)}개 기관</div>',
        unsafe_allow_html=True
    )

    if not api_benefits:
        st.markdown(
            '<div class="no-result">🔎 검색 결과가 없습니다. 다른 키워드나 분야를 선택해 보세요.</div>',
            unsafe_allow_html=True
        )
    else:
        for category in sorted(grouped.keys()):
            items = grouped[category]
            icon = MINISTRY_ICON.get(category, "🏢")
            with st.expander(f"{icon} {category}  —  {len(items)}개 서비스", expanded=False):
                for b in items:
                    url_html = (
                        f'<a href="{b["url"]}" target="_blank" '
                        f'style="color:#2C4A8A;font-weight:600;margin-left:8px;">🔗 자세히 보기</a>'
                        if b.get("url") else ""
                    )
                    region_label = b.get("region", "전국공통")
                    user_cat = b.get("user_category", "기타")
                    cat_icon = CAT_ICON.get(user_cat, "📌")
                    st.markdown(f"""
                    <div class="benefit-card">
                        <div class="benefit-title">{b['name']}</div>
                        <div class="benefit-desc">{b['description']}</div>
                        <div class="tags">
                            <span class="tag tag-cat">{cat_icon} {user_cat}</span>
                            <span class="tag tag-region">🗺️ {region_label}</span>
                        </div>
                        <div class="apply-row">📍 {b['apply_where']} {url_html}</div>
                    </div>
                    """, unsafe_allow_html=True)


# ── 자격 확인 ──────────────────────────────────────────────────────────────
def render_eligibility():
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

    with st.form("profile_form"):
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

        st.markdown('<div class="form-section-title">💰 소득·재산</div>', unsafe_allow_html=True)
        st.caption("※ 자녀와 함께 거주하셔도 기초연금·장기요양 등 대부분 어르신 혜택은 본인(+배우자) 소득과 재산만 판정에 반영됩니다.")
        col1, col2 = st.columns(2)
        with col1:
            income_opts = ["월 50만원 미만", "월 50~100만원", "월 100~200만원", "월 200만원 이상"]
            income = st.selectbox("본인(+배우자) 월소득 (자녀 소득 제외)", income_opts,
                index=income_opts.index(saved.get("income", "월 50~100만원")))
        with col2:
            home_opts = ["자가(본인 소유)", "전세", "월세·보증금", "자녀 명의 주택 거주 (본인 무주택)", "무주택(무료 거주 등)"]
            saved_home = saved.get("home_ownership", "자가(본인 소유)")
            if saved_home not in home_opts:
                saved_home = "자가(본인 소유)"
            home_ownership = st.selectbox("주택 소유 현황 (본인·배우자 명의 기준)", home_opts,
                index=home_opts.index(saved_home))

        asset_opts = ["2천만원 미만", "2천만~5천만원", "5천만~1억원", "1억~2억원", "2억~3억원", "3억 이상"]
        saved_asset = saved.get("asset_level", "2천만원 미만")
        if saved_asset not in asset_opts:
            saved_asset = "2천만원 미만"
        asset_level = st.selectbox("본인(+배우자) 재산 (부동산+금융자산, 자녀 자산 제외)", asset_opts,
            index=asset_opts.index(saved_asset))

        st.markdown('<div class="form-section-title">🏥 건강·장애</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            disability_opts = ["없음", "경증장애", "중증장애"]
            disability = st.selectbox("장애 여부", disability_opts,
                index=disability_opts.index(saved.get("disability", "없음")))
        with col2:
            st.write("")  # 레이블 높이 맞춤

        health_opts = [
            "만성질환 (고혈압·당뇨·관절염 등)",
            "암 (악성 종양)",
            "뇌졸중·심뇌혈관질환",
            "파킨슨병·희귀질환",
            "치매 진단 또는 의심",
            "거동 불편 (이동·일상생활 어려움)",
            "정신건강 어려움 (우울증·불안 등)",
        ]
        saved_health = saved.get("health_condition", [])
        if isinstance(saved_health, str):
            saved_health = [saved_health] if saved_health and saved_health != "특이사항 없음" else []
        saved_health = [h for h in saved_health if h in health_opts]
        health_condition = st.multiselect(
            "주요 건강 상태 (해당 항목 모두 선택, 없으면 빈칸)", health_opts,
            default=saved_health,
        )

        st.markdown('<div class="form-section-title">📋 기타</div>', unsafe_allow_html=True)
        veteran_opts = ["없음", "국가유공자", "참전유공자"]
        saved_veteran = saved.get("veteran", "없음")
        if saved_veteran not in veteran_opts:
            saved_veteran = "없음"
        veteran = st.selectbox("국가·참전유공자 여부", veteran_opts,
            index=veteran_opts.index(saved_veteran))

        notes = st.text_area("추가 사항 (선택)", value=saved.get("notes", ""),
            placeholder="예: 기초생활수급자, 의료급여 대상자, 독거노인 등")

        st.markdown("""
<div style="background:#F0F4FA;border-left:4px solid #2C4A8A;border-radius:8px;
            padding:12px 16px;margin:20px 0 8px 0;font-size:0.85rem;color:#4A5568;line-height:1.6;">
    ℹ️ <b>자격 확인 안내</b><br>
    AI 자격 확인은 주요 복지서비스 <b>45개</b>를 대상으로 분석합니다.
    그 외 복지혜택은 <b>혜택조회</b> 메뉴에서 전체 목록을 확인하세요.
</div>
""", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("🔍 자격 확인하기", use_container_width=True, type="primary")
        with col2:
            save_btn = st.form_submit_button("💾 정보 저장하기", use_container_width=True)

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

    if submitted:
        save_profile(user_profile)
        st.markdown('<div class="result-section-title">📊 AI 자격 분석 결과</div>', unsafe_allow_html=True)

        with st.spinner(f"AI가 {len(TOP_BENEFITS)}개 혜택을 분석하는 중입니다... (약 20~30초 소요)"):
            results = check_all_eligibility(user_profile, TOP_BENEFITS)
        save_eligibility_results(results)

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

        grouped = defaultdict(list)
        for b in TOP_BENEFITS:
            user_cat = TOP_TO_USER_CAT.get(b["category"], "기타")
            grouped[user_cat].append(b)

        def cat_sort_key(cat):
            return (0 if any(results.get(b["name"], {}).get("status") == "가능"
                             for b in grouped[cat]) else 1, cat)

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


# ── 신청 안내 ──────────────────────────────────────────────────────────────
def render_guide():
    st.markdown("""
    <div class="page-header">
        <h2>📋 신청 안내</h2>
        <p>자격 확인된 혜택의 신청 방법을 단계별로 안내해 드립니다</p>
    </div>
    """, unsafe_allow_html=True)

    eligibility  = load_eligibility_results()
    user_profile = load_profile()
    bookmarks    = load_bookmarks()

    possible_names = [b["name"] for b in TOP_BENEFITS if eligibility.get(b["name"], {}).get("status") == "가능"]
    check_names    = [b["name"] for b in TOP_BENEFITS if eligibility.get(b["name"], {}).get("status") == "확인필요"]
    all_names      = [b["name"] for b in TOP_BENEFITS]

    if eligibility:
        st.markdown(
            f'<div class="info-banner">✅ 자격확인 결과: <b>가능 {len(possible_names)}개</b>, '
            f'확인필요 {len(check_names)}개 — 가능 혜택을 우선 표시합니다</div>',
            unsafe_allow_html=True
        )
        view_mode = st.radio(
            "표시 범위", ["✅ 가능 혜택만", "⚠️ 확인필요 포함", "📋 전체 목록"],
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

    benefit_map = {b["name"]: b for b in TOP_BENEFITS}

    st.markdown(
        '<div style="font-size:1rem;font-weight:700;color:#1B2A4A;margin-bottom:6px;">'
        '👇 아래 목록에서 신청할 혜택을 선택하신 후 <span style="color:#2C4A8A;">📖 신청 방법 알아보기</span> 버튼을 눌러주세요'
        '</div>',
        unsafe_allow_html=True
    )

    def _label(name):
        res = eligibility.get(name, {})
        status = res.get("status", "")
        bm = bookmarks.get(name, "")
        icons = ""
        if status == "가능": icons += "✅ "
        elif status == "확인필요": icons += "⚠️ "
        if bm: icons += BOOKMARK_ICON.get(bm, "") + " "
        return icons + name

    labeled = [_label(n) for n in display_names]
    selected_label = st.selectbox("혜택 선택", labeled, label_visibility="collapsed")
    selected = display_names[labeled.index(selected_label)]
    benefit = benefit_map.get(selected, {})

    res = eligibility.get(selected, {})
    status = res.get("status", "")
    reason = res.get("reason", "")
    user_cat = TOP_TO_USER_CAT.get(benefit.get("category", ""), "기타")
    cat_icon = CAT_ICON.get(user_cat, "📌")

    if status:
        sty = {"가능": ("chip-possible", "✅"), "확인필요": ("chip-check", "⚠️"), "불가": ("", "❌")}.get(status, ("chip-all", ""))
        st.markdown(
            f'<span class="benefit-chip {sty[0]}">{sty[1]} {status}</span>'
            f'<span class="benefit-chip chip-all">{cat_icon} {user_cat}</span>'
            + (f'　<span style="font-size:0.88rem;color:#7F8C9A;">{reason}</span>' if reason else ""),
            unsafe_allow_html=True
        )

    if st.button("📖 신청 방법 알아보기", use_container_width=True, type="primary"):
        with st.spinner("신청 방법을 준비하고 있습니다..."):
            guide = get_application_guide(selected, user_profile if user_profile else None)
        st.markdown(f"""
        <div class="guide-card">
            <div class="guide-title">📌 {selected} 신청 방법</div>
            {guide}
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    bm_current = bookmarks.get(selected, "")
    st.markdown('<div class="status-card-title">📌 신청 진행 상태 기록</div>', unsafe_allow_html=True)
    st.markdown('위에서 선택한 신청가능 혜택의 상태를 지정하고 <b>상태 저장</b>을 누르세요.', unsafe_allow_html=True)

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
        st.write("")
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

    if bookmarks:
        st.markdown('<div class="section-divider">📋 내 신청 진행 현황</div>', unsafe_allow_html=True)
        st.caption("혜택별로 기록해 둔 신청 진행 상태입니다.")
        for bm_status in BOOKMARK_OPTS:
            names_in = [n for n, s in bookmarks.items() if s == bm_status]
            if names_in:
                icon = BOOKMARK_ICON.get(bm_status, "")
                desc = {"관심": "더 알아볼 예정", "신청예정": "곧 신청할 것", "완료": "이미 신청함"}.get(bm_status, "")
                st.markdown(f"**{icon} {bm_status}** ({desc}) — {len(names_in)}개: " + " · ".join(names_in))

    st.markdown('<div class="section-divider">💬 AI 상담</div>', unsafe_allow_html=True)
    st.caption("복지혜택, 자격 조건, 신청 방법 등 궁금한 점을 질문하세요")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    for msg in st.session_state.chat_history:
        st.chat_message(msg["role"]).write(msg["content"])
    if prompt := st.chat_input(f"예: '{selected}' 신청 시 필요한 서류가 뭔가요?"):
        st.chat_message("user").write(prompt)
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        context = f"현재 '{selected}' 혜택의 신청 방법을 알아보는 중입니다. " if selected else ""
        with st.spinner("답변 작성 중..."):
            response = ask_claude(context + prompt, st.session_state.chat_history[:-1])
        st.chat_message("assistant").write(response)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
