"""청소년·대학생 복지 전용 렌더링 모듈 — 혜택조회 / 자격확인 / 신청안내"""
import json as _json
import streamlit as st
from collections import defaultdict

from utils.welfare_api import (
    TOP_YOUTH_BENEFITS, YOUTH_CATEGORIES, YOUTH_TO_USER_CAT, REGIONS,
    get_youth_benefits_by_region,
)
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
    "학비·장학금": "📚", "생활비지원": "🛒", "주거": "🏠",
    "일자리·취업": "💼", "건강·심리": "🏥", "문화·여가": "🎭",
    "자립지원": "🤝", "창업·금융": "💰", "기타": "📌",
}

BOOKMARK_OPTS = ["관심", "신청예정", "완료"]
BOOKMARK_ICON = {"관심": "⭐", "신청예정": "📌", "완료": "✔️"}

STATUS_STYLE = {
    "가능":    {"color": "#1B5E20", "icon": "✅"},
    "불가":    {"color": "#B71C1C", "icon": "❌"},
    "확인필요": {"color": "#7D6608", "icon": "⚠️"},
}

CURRENT_YEAR = 2026

# TOP_YOUTH_BENEFITS 변경 시 자동 캐시 무효화를 위한 버전 문자열
_YOUTH_BENEFITS_VER = f"{len(TOP_YOUTH_BENEFITS)}_{TOP_YOUTH_BENEFITS[-1]['id']}"


@st.cache_data(ttl=7*24*3600, show_spinner=False)
def _cached_youth_eligibility(profile_json: str, region: str, _ver: str) -> dict:
    """st.cache_data 메모리 캐시 — 동일 프로필+지역은 AI 호출 없이 즉시 반환."""
    profile = _json.loads(profile_json)
    region_benefits = [b for b in TOP_YOUTH_BENEFITS
                       if b.get("region", "전국공통") in ("전국공통", region)]
    return check_all_eligibility(profile, region_benefits)


@st.cache_data(ttl=3600)
def _load_youth_benefits(region: str):
    return get_youth_benefits_by_region(region)


# ── 혜택 조회 ──────────────────────────────────────────────────────────────
def render_benefits():
    st.markdown("""
    <div class="page-header-youth">
        <h2>🎓 청소년·대학생 복지혜택 조회</h2>
        <p>만 15~24세 청소년·대학생을 위한 복지혜택 목록입니다</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        selected_region = st.selectbox("🗺️ 지역 선택", REGIONS, index=0)
    with col2:
        cat_options = ["전체"] + YOUTH_CATEGORIES
        selected_cat = st.selectbox("📂 분야 선택", cat_options, index=0)

    search_query = st.text_input(
        "검색", placeholder="🔍  서비스명 또는 내용으로 검색하세요  예) 장학금, 월세, 취업",
        label_visibility="collapsed"
    )

    all_api_benefits, debug_msg = _load_youth_benefits(selected_region)
    st.caption(debug_msg)
    st.divider()

    # 주요 혜택 (지역 필터 포함: 전국공통 + 선택 지역만 표시)
    top_filtered = [b for b in TOP_YOUTH_BENEFITS
                    if b.get("region", "전국공통") in ("전국공통", selected_region)
                    and (selected_cat == "전체" or YOUTH_TO_USER_CAT.get(b["category"]) == selected_cat)
                    and (not search_query or search_query.lower() in b["name"].lower()
                         or search_query.lower() in b.get("description", "").lower())]

    if top_filtered:
        st.markdown('<div class="section-title-youth">🎓 주요 청소년·대학생 혜택</div>', unsafe_allow_html=True)
        for b in top_filtered:
            user_cat = YOUTH_TO_USER_CAT.get(b["category"], "기타")
            cat_icon = CAT_ICON.get(user_cat, "📌")
            age_text = f"{b['age_min']}~{b.get('age_max', '')}세" if b.get("age_max") else f"{b['age_min']}세 이상"
            st.markdown(f"""
            <div class="top-card-youth">
                <div class="benefit-title">{b['name']}</div>
                <div class="benefit-desc">{b['description']}</div>
                <div class="tags">
                    <span class="tag tag-youth">🎓 청소년·대학생</span>
                    <span class="tag tag-cat">{cat_icon} {user_cat}</span>
                    <span class="tag tag-amount">💰 {b['amount']}</span>
                    <span class="tag tag-target">👤 {age_text} · {b['income_level']}</span>
                    <span class="tag tag-region">🗺️ 전국공통</span>
                </div>
                <div class="apply-row">📍 {b['apply_where']}</div>
            </div>
            """, unsafe_allow_html=True)

    # API 전체 서비스
    st.markdown('<div class="section-title-youth">📋 복지로 API 청소년 관련 서비스</div>', unsafe_allow_html=True)
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
                        f'style="color:#2E7D52;font-weight:600;margin-left:8px;">🔗 자세히 보기</a>'
                        if b.get("url") else ""
                    )
                    region_label = b.get("region", "전국공통")
                    user_cat = b.get("user_category", "기타")
                    cat_icon = CAT_ICON.get(user_cat, "📌")
                    st.markdown(f"""
                    <div class="benefit-card-youth">
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
    <div class="page-header" style="background:linear-gradient(135deg,#1A3A2A 0%,#2E7D52 100%);">
        <h2>🎓 청소년·대학생 자격 확인</h2>
        <p>내 정보를 입력하시면 AI가 받을 수 있는 청소년·대학생 혜택을 분석해 드립니다</p>
    </div>
    """, unsafe_allow_html=True)

    saved = load_profile()
    if saved:
        st.markdown('<div class="saved-notice">💾 이전에 저장한 정보가 있습니다</div>', unsafe_allow_html=True)
        if st.button("❌ 저장 정보 삭제"):
            delete_profile()
            st.rerun()

    # st.form 없이 렌더링 — 가족상황/거주형태 변경 시 소득 레이블 즉시 반응
    st.markdown('<div class="form-section-title">👤 기본 정보</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        birth_year = st.number_input(
            "태어난 년도", min_value=2002, max_value=2011,
            value=saved.get("birth_year", 2006), step=1,
            help="만 15~24세 (2002~2011년생)"
        )
        age = CURRENT_YEAR - birth_year
        st.markdown(f'<div class="age-display">만 {age}세</div>', unsafe_allow_html=True)
    with col2:
        gender_opts = ["남성", "여성"]
        gender = st.selectbox("성별", gender_opts,
            index=gender_opts.index(saved.get("gender", "남성")))

    col1, col2 = st.columns(2)
    with col1:
        saved_region = saved.get("region", "전국공통")
        region = st.selectbox(
            "거주 지역",
            REGIONS,
            index=REGIONS.index(saved_region) if saved_region in REGIONS else 0,
            help="서울·경기 등 지역 전용 혜택 포함 여부에 영향을 줍니다",
        )
    with col2:
        st.write("")  # 레이아웃 균형

    st.markdown('<div class="form-section-title">📚 학적 정보</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        school_opts = ["고등학생 재학 중", "대학교 재학 중", "대학원 재학 중",
                       "졸업·수료", "휴학 중", "미진학·기타"]
        school_status = st.selectbox("학적 현황", school_opts,
            index=school_opts.index(saved.get("school_status", "대학교 재학 중"))
            if saved.get("school_status") in school_opts else 1)
    with col2:
        grade_opts = ["1학년", "2학년", "3학년", "4학년", "5학년 이상", "해당없음"]
        grade = st.selectbox("학년", grade_opts,
            index=grade_opts.index(saved.get("grade", "1학년"))
            if saved.get("grade") in grade_opts else 0)

    family_opts = [
        "양부모 함께 거주 (혼인 유지)",
        "한부모 가정 (사별·이혼 등)",
        "이혼 — 부모 각각 따로 거주",
        "독립 자취 (부모와 별거)",
        "보호시설·기타",
    ]
    family_situation = st.selectbox(
        "가족 상황", family_opts,
        index=family_opts.index(saved.get("family_situation", "양부모 함께 거주 (혼인 유지)"))
        if saved.get("family_situation") in family_opts else 0,
    )

    col1, col2 = st.columns(2)
    with col1:
        income_decile_opts = [
            "1~2구간 — 월 286만원 이하 (기초·차상위)",
            "3~4구간 — 월 286~515만원",
            "5~6구간 — 월 515~744만원",
            "7~8구간 — 월 744~1,144만원",
            "9구간 — 월 1,144~1,716만원",
            "10구간 — 월 1,716만원 초과",
            "모름 (잘 모르겠어요)",
        ]
        income_decile = st.selectbox(
            "가구 소득분위 (장학금 기준, 4인 가구 기준)",
            income_decile_opts,
            index=income_decile_opts.index(saved.get("income_decile", "모름 (잘 모르겠어요)"))
            if saved.get("income_decile") in income_decile_opts else 6,
        )
    with col2:
        household_opts = ["부모님과 함께 거주", "독립(자취·기숙사)", "보호시설 거주", "기타"]
        household = st.selectbox("거주 형태", household_opts,
            index=household_opts.index(saved.get("household", "부모님과 함께 거주"))
            if saved.get("household") in household_opts else 0)

    with st.expander("📌 소득분위 기준 자세히 보기 (4인 가구 월 소득인정액 기준)", expanded=False):
        st.markdown("""
| 구간 | 월 소득인정액 (4인 가구 기준) | 기준 중위소득 |
|------|-------------------------------|--------------|
| **1구간** | 171만원 이하 | 30% 이하 |
| **2구간** | 171 ~ 286만원 | 30 ~ 50% |
| **3구간** | 286 ~ 400만원 | 50 ~ 70% |
| **4구간** | 400 ~ 515만원 | 70 ~ 90% |
| **5구간** | 515 ~ 572만원 | 90 ~ 100% |
| **6구간** | 572 ~ 744만원 | 100 ~ 130% |
| **7구간** | 744 ~ 858만원 | 130 ~ 150% |
| **8구간** | 858 ~ 1,144만원 | 150 ~ 200% |
| **9구간** | 1,144 ~ 1,716만원 | 200 ~ 300% |
| **10구간** | 1,716만원 초과 | 300% 초과 |
""")
        st.caption("※ 소득인정액 = 월 소득 + 재산의 소득환산액. 정확한 구간 확인은 한국장학재단(www.kosaf.go.kr)에서 모의계산 가능합니다.")
        st.markdown("**가족 상황별 소득 산정 기준**")
        st.markdown("""
| 가족 상황 | 소득 산정 기준 |
|-----------|---------------|
| 양부모 함께 거주 | 부모 두 분의 소득 합산 |
| 한부모 가정 (사별·이혼) | 함께 사는 부모 한 분의 소득 |
| 이혼 — 부모 각각 거주 | 주민등록상 같은 주소의 부모 한 쪽만 |
| 독립 자취 — 장학금 신청 시 | 미혼·만 30세 미만이면 부모 소득 포함 |
| 독립 자취 — 복지혜택 신청 시 | 독립 세대주이면 본인 소득만 기준 |
| 보호시설·기타 | 본인 소득만 (부모 소득 미포함) |
""")
        st.caption("※ 장학금과 복지혜택은 소득 산정 기준이 다릅니다. 독립 자취 중이라면 신청하는 혜택에 따라 기준을 별도로 확인하세요.")

    st.markdown('<div class="form-section-title">💰 소득·생활</div>', unsafe_allow_html=True)

    _independent = (
        family_situation in ("독립 자취 (부모와 별거)", "보호시설·기타")
        or household in ("독립(자취·기숙사)", "보호시설 거주")
    )
    income_label = "본인 월소득 (세전)" if _independent else "가구 월소득 (세전, 부모 포함)"

    col1, col2 = st.columns(2)
    with col1:
        income_opts = [
            "소득 없음 (무소득·실직 등)",
            "월 200만원 미만",
            "월 200~400만원",
            "월 400~600만원",
            "월 600~900만원",
            "월 900만원 이상",
        ]
        income = st.selectbox(
            income_label, income_opts,
            index=income_opts.index(saved.get("income", "월 400~600만원"))
            if saved.get("income") in income_opts else 3,
        )
    with col2:
        welfare_opts = ["없음", "기초생활수급자", "차상위계층", "한부모가족"]
        welfare_status = st.selectbox("수급·지원 현황", welfare_opts,
            index=welfare_opts.index(saved.get("welfare_status", "없음"))
            if saved.get("welfare_status") in welfare_opts else 0)

    st.markdown('<div class="form-section-title">📋 기타</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        disability_opts = ["없음", "경증장애", "중증장애"]
        disability = st.selectbox("장애 여부", disability_opts,
            index=disability_opts.index(saved.get("disability", "없음"))
            if saved.get("disability") in disability_opts else 0)
    with col2:
        protection_opts = ["해당없음", "자립준비청년(보호종료)"]
        protection = st.selectbox("보호종료 청년 여부", protection_opts,
            index=protection_opts.index(saved.get("protection", "해당없음"))
            if saved.get("protection") in protection_opts else 0)

    notes = st.text_area("추가 사항 (선택)", value=saved.get("notes", ""),
        placeholder="예: 다자녀가구, 농어촌 거주, 특기사항 등")

    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        submitted = st.button("🔍 자격 확인하기", use_container_width=True, type="primary")
    with col2:
        save_btn = st.button("💾 정보 저장하기", use_container_width=True)

    user_profile = {
        "birth_year": birth_year, "age": age, "gender": gender,
        "region": region,
        "school_status": school_status, "grade": grade,
        "income_decile": income_decile, "household": household,
        "family_situation": family_situation,
        "income": income, "welfare_status": welfare_status,
        "disability": disability, "protection": protection,
        "notes": notes,
    }

    if save_btn:
        save_profile(user_profile)
        st.success("✅ 정보가 저장되었습니다. 다음 방문 시 자동으로 불러옵니다.")

    if submitted:
        save_profile(user_profile)
        st.markdown('<div class="result-section-title">📊 AI 자격 분석 결과</div>', unsafe_allow_html=True)

        # 사용자 거주 지역에 맞는 혜택만 분석 (전국공통 + 해당 지역)
        user_region = user_profile.get("region", "전국공통")
        region_benefits = [b for b in TOP_YOUTH_BENEFITS
                           if b.get("region", "전국공통") in ("전국공통", user_region)]

        with st.spinner(f"AI가 {len(region_benefits)}개 혜택을 분석하는 중입니다... (약 20~30초 소요)"):
            results = _cached_youth_eligibility(
                _json.dumps(user_profile, ensure_ascii=False, sort_keys=True),
                user_region,
                _YOUTH_BENEFITS_VER,
            )
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
        for b in region_benefits:
            user_cat = YOUTH_TO_USER_CAT.get(b["category"], "기타")
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
                    age_text = f"{b['age_min']}~{b.get('age_max', '')}세" if b.get("age_max") else f"{b['age_min']}세 이상"
                    st.markdown(f"""
                    <div class="result-detail">
                        <b style="color:{sty['color']};">{sty['icon']} {status}</b> &nbsp; {reason}
                        <br><br>
                        <span style="color:#4A5568;font-size:0.9rem;">{b['description']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    st.caption(f"📍 신청: {b['apply_where']}  ·  대상: {age_text}, {b['income_level']}")


# ── 신청 안내 ──────────────────────────────────────────────────────────────
def render_guide():
    st.markdown("""
    <div class="page-header" style="background:linear-gradient(135deg,#1A3A2A 0%,#2E7D52 100%);">
        <h2>🎓 청소년·대학생 신청 안내</h2>
        <p>자격 확인된 혜택의 신청 방법을 단계별로 안내해 드립니다</p>
    </div>
    """, unsafe_allow_html=True)

    eligibility  = load_eligibility_results()
    user_profile = load_profile()
    bookmarks    = load_bookmarks()

    possible_names = [b["name"] for b in TOP_YOUTH_BENEFITS if eligibility.get(b["name"], {}).get("status") == "가능"]
    check_names    = [b["name"] for b in TOP_YOUTH_BENEFITS if eligibility.get(b["name"], {}).get("status") == "확인필요"]
    all_names      = [b["name"] for b in TOP_YOUTH_BENEFITS]

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

    benefit_map = {b["name"]: b for b in TOP_YOUTH_BENEFITS}

    st.markdown(
        '<div style="font-size:1rem;font-weight:700;color:#1A3A2A;margin-bottom:6px;">'
        '👇 아래 목록에서 신청할 혜택을 선택하신 후 <span style="color:#2E7D52;">📖 신청 방법 알아보기</span> 버튼을 눌러주세요'
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
    user_cat = YOUTH_TO_USER_CAT.get(benefit.get("category", ""), "기타")
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
