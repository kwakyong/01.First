import hashlib
import json
import os
import time
from pathlib import Path
from openai import AzureOpenAI
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent
load_dotenv(BASE_DIR / ".env", override=True)
if not os.getenv("AZURE_OPENAI_API_KEY"):
    load_dotenv(BASE_DIR / ".env.example", override=True)


def _secret(key: str, default: str = "") -> str:
    """로컬 .env 또는 Streamlit Cloud secrets 에서 값을 읽습니다."""
    try:
        import streamlit as st
        return st.secrets.get(key, os.getenv(key, default))
    except Exception:
        return os.getenv(key, default)


client = AzureOpenAI(
    api_key=_secret("AZURE_OPENAI_API_KEY"),
    azure_endpoint=_secret("AZURE_OPENAI_ENDPOINT"),
    api_version=_secret("AZURE_OPENAI_API_VERSION", "2024-02-01"),
)

DEPLOYMENT_NAME = _secret("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")

# 2024년 기준 중위소득 (월, 원) — 소득 기준 % 계산용
_SENIOR_MEDIAN_INCOME = {
    "1인": 2_228_445,
    "2인": 3_682_609,
    "3인": 4_714_657,
    "4인 이상": 5_729_913,
}
_INCOME_RANGE_SENIOR = {
    "월 50만원 미만":  (0,           490_000),
    "월 50~100만원":   (500_000,     990_000),
    "월 100~200만원":  (1_000_000, 1_990_000),
    "월 200만원 이상": (2_000_000, 9_999_999),
}

# ── 결과 캐시 ──────────────────────────────────────────────────────────────────
_CACHE_DIR = BASE_DIR / "cache"
_CACHE_TTL = 7 * 24 * 3600  # 7일


def _cache_key(user_profile: dict, benefits: list) -> str:
    """프로필 + 혜택 목록 조합으로 고유 캐시 키 생성."""
    fields = {
        "age":             user_profile.get("age"),
        "gender":          user_profile.get("gender"),
        "household":       user_profile.get("household"),
        "household_size":  user_profile.get("household_size"),
        "income":          user_profile.get("income"),
        "home_ownership":  user_profile.get("home_ownership"),
        "asset_level":     user_profile.get("asset_level"),
        "disability":      user_profile.get("disability"),
        "health_condition": sorted(user_profile.get("health_condition", []))
                            if isinstance(user_profile.get("health_condition"), list)
                            else [user_profile.get("health_condition", "")],
        "veteran":         user_profile.get("veteran"),
        "school_status":   user_profile.get("school_status"),
        "income_decile":   user_profile.get("income_decile"),
        "region":          user_profile.get("region"),
        "family_situation":user_profile.get("family_situation"),
        "benefit_ids":     sorted(b.get("id", b["name"]) for b in benefits),
    }
    raw = json.dumps(fields, ensure_ascii=False, sort_keys=True)
    return hashlib.md5(raw.encode()).hexdigest()


def _load_cache(key: str):
    """캐시 파일 로드. TTL 초과 또는 없으면 None 반환."""
    _CACHE_DIR.mkdir(exist_ok=True)
    f = _CACHE_DIR / f"{key}.json"
    if not f.exists():
        return None
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
        if time.time() - data.get("ts", 0) > _CACHE_TTL:
            f.unlink(missing_ok=True)
            return None
        return data["results"]
    except Exception:
        return None


def _save_cache(key: str, results: dict):
    """결과를 캐시 파일로 저장."""
    _CACHE_DIR.mkdir(exist_ok=True)
    f = _CACHE_DIR / f"{key}.json"
    f.write_text(
        json.dumps({"ts": time.time(), "results": results}, ensure_ascii=False),
        encoding="utf-8",
    )

SYSTEM_PROMPT = """당신은 대한민국 사회복지 전문 상담사입니다.
60대 이상 어르신들이 이해하기 쉽도록 쉬운 말로, 천천히, 친절하게 설명해주세요.
복잡한 용어는 피하고, 핵심 내용만 간단명료하게 답변하세요.
복지 혜택의 자격 조건, 신청 방법, 필요 서류 등을 안내할 수 있습니다."""


def ask_claude(user_message: str, chat_history: list = None) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if chat_history:
        messages.extend(chat_history)
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=messages,
        max_tokens=1024,
    )
    return response.choices[0].message.content


def check_eligibility(user_profile: dict, benefit_name: str) -> str:
    prompt = f"""아래 어르신의 정보를 바탕으로 '{benefit_name}' 혜택을 받을 수 있는지 판단해주세요.

[어르신 정보]
- 나이: {user_profile.get('age', '미입력')}세
- 가구 유형: {user_profile.get('household', '미입력')}
- 월 소득: {user_profile.get('income', '미입력')}
- 장애 여부: {user_profile.get('disability', '없음')}
- 기타: {user_profile.get('notes', '없음')}

자격 여부를 ✅ 가능 / ❌ 어려움 / ❓ 확인 필요 중 하나로 먼저 표시하고,
그 이유를 2-3줄로 쉽게 설명해주세요."""

    return ask_claude(prompt)


def check_all_eligibility(user_profile: dict, benefits: list) -> dict:
    """
    TOP_BENEFITS 전체를 단 1회 AI 호출로 자격 분석.
    반환: {서비스명: {"status": "가능"|"불가"|"확인필요", "reason": str}}
    동일 프로필+혜택 조합은 7일간 캐시에서 즉시 반환.
    """
    key = _cache_key(user_profile, benefits)
    cached = _load_cache(key)
    if cached is not None:
        return cached

    def _age_range(b):
        mn = b.get("age_min", 0)
        mx = b.get("age_max")
        return f"{mn}~{mx}세" if mx else f"{mn}세 이상"

    is_youth = "school_status" in user_profile

    # ── 어르신: 건강 조건 사전 필터 + 소득% 범위 계산 ────────────────────────
    pre_disqualified = {}
    benefits_to_analyze = benefits
    _income_pct = ""
    _hh_key = "1인"

    if not is_youth:
        user_health = user_profile.get("health_condition", [])
        if isinstance(user_health, str):
            user_health = [user_health] if user_health else []

        benefits_to_analyze = []
        for b in benefits:
            req = b.get("required_health", [])
            if req and not any(h in user_health for h in req):
                pre_disqualified[b["name"]] = {"status": "불가", "reason": "건강 조건 미해당"}
            else:
                benefits_to_analyze.append(b)

        _hh = user_profile.get("household", "")
        _hh_key = "2인" if _hh == "부부가구" else "1인"
        _base = _SENIOR_MEDIAN_INCOME[_hh_key]
        _income_str = user_profile.get("income", "")
        _lo, _hi = _INCOME_RANGE_SENIOR.get(_income_str, (1_000_000, 1_990_000))
        if _income_str == "월 200만원 이상":
            _income_pct = f"중위소득 {round(_lo / _base * 100)}% 이상 ({_hh_key}가구 기준)"
        else:
            _income_pct = f"중위소득 {round(_lo / _base * 100)}~{round(_hi / _base * 100)}% ({_hh_key}가구 기준)"

    # ── benefit_lines ─────────────────────────────────────────────────────────
    benefit_lines = "\n".join(
        f"- {b['name']} | 나이:{_age_range(b)} | 소득:{b.get('income_level','전체')} | {b.get('description','')[:40]}"
        for b in benefits_to_analyze
    )

    # ── profile_lines + system_msg ────────────────────────────────────────────
    if is_youth:
        profile_lines = (
            f"나이: {user_profile.get('age')}세 / "
            f"성별: {user_profile.get('gender','미입력')} / "
            f"거주지역: {user_profile.get('region','전국공통')} / "
            f"학적현황: {user_profile.get('school_status','미입력')} / "
            f"학년: {user_profile.get('grade','미입력')} / "
            f"가족상황: {user_profile.get('family_situation','미입력')} / "
            f"거주형태: {user_profile.get('household','미입력')} / "
            f"가구소득분위(장학금기준): {user_profile.get('income_decile','미입력')} / "
            f"월소득: {user_profile.get('income','미입력')} / "
            f"수급현황: {user_profile.get('welfare_status','없음')} / "
            f"장애여부: {user_profile.get('disability','없음')} / "
            f"보호종료청년: {user_profile.get('protection','해당없음')} / "
            f"기타: {user_profile.get('notes','없음')}"
        )
        system_msg = (
            "당신은 대한민국 청소년·대학생 복지 및 장학금 자격 분석 전문가입니다. "
            "다음 규칙을 반드시 따르세요:\n"
            "1. 나이 범위가 명시된 혜택(예: 16~16세)은 해당 나이가 아니면 '불가'로 판단하세요.\n"
            "2. 학적 조건이 있는 혜택(예: 고등학교 1학년 전용)은 학적현황이 맞지 않으면 '불가'로 판단하세요.\n"
            "3. 소득 판단 기준 구분:\n"
            "   - 장학금(국가장학금·근로장학금·학자금대출 등): '가구소득분위(장학금기준)' 값을 사용하세요.\n"
            "   - 복지혜택(마음건강·주거·생활비지원 등): '월소득' 값을 사용하세요. 가구소득분위는 무시하세요.\n"
            "4. '월소득: 소득 없음'이면 복지혜택 소득 기준은 대부분 충족합니다.\n"
            "5. 가구소득분위 1~2구간이면 국가장학금·근로장학금·생활비대출은 '가능'으로 판단하세요.\n"
            "6. 명백히 기준 미달인 경우에만 '불가', 불분명한 경우는 '확인필요'로 판단하세요.\n"
            "반드시 JSON만 출력하고 다른 설명은 쓰지 마세요."
        )
    else:
        _hc = user_profile.get('health_condition', [])
        _hc_str = ", ".join(_hc) if isinstance(_hc, list) else (_hc or "특이사항 없음")
        if not _hc_str:
            _hc_str = "특이사항 없음"
        profile_lines = (
            f"나이: {user_profile.get('age')}세 / "
            f"성별: {user_profile.get('gender','미입력')} / "
            f"가구유형: {user_profile.get('household','미입력')} / "
            f"가구원수: {user_profile.get('household_size','미입력')} / "
            f"월소득(본인+배우자, 자녀제외): {user_profile.get('income','미입력')} / "
            f"소득중위%: {_income_pct} / "
            f"주택소유(본인+배우자명의): {user_profile.get('home_ownership','미입력')} / "
            f"재산(본인+배우자, 자녀제외): {user_profile.get('asset_level','미입력')} / "
            f"장애여부: {user_profile.get('disability','없음')} / "
            f"건강상태: {_hc_str} / "
            f"본인사업자: {user_profile.get('own_business','없음')} / "
            f"배우자사업자: {user_profile.get('spouse_business','없음')} / "
            f"국가유공자: {user_profile.get('veteran','없음')} / "
            f"기타: {user_profile.get('notes','없음')}"
        )
        system_msg = (
            "당신은 대한민국 어르신 복지 자격 분석 전문가입니다. "
            "다음 규칙을 반드시 따르세요:\n"
            "1. 소득·재산 판정은 어르신 본인+배우자 기준이며 자녀 소득·재산은 포함되지 않습니다.\n"
            "2. '자녀 명의 주택 거주 (본인 무주택)'은 무주택으로 간주하여 주거 혜택에 유리하게 판단하세요.\n"
            "3. 소득 기준 판단 — 프로필의 '소득중위%' 범위와 혜택 소득 기준 %를 비교하세요:\n"
            "   - 소득중위% 최대값이 혜택 기준보다 낮으면 → '가능'\n"
            "   - 소득중위% 최솟값이 혜택 기준보다 높으면 → '불가'\n"
            "   - 범위가 혜택 기준에 걸쳐있으면 → '확인필요'\n"
            "   예) 소득 45~89%, 100% 이하 기준 → 가능 / 소득 45~89%, 40% 이하 기준 → 불가\n"
            "4. 소득 기준이 '전체', '건강보험 가입자 전체', 또는 '우선 배정'이 포함된 경우 소득과 무관하게 '가능'입니다.\n"
            "5. 장애여부가 '없음'이면 장애 관련 혜택(장애인연금·장애수당·활동지원 등)은 '불가'로 판단하세요.\n"
            "6. 나이가 혜택 최소 나이에 미달이면 '불가'로 판단하세요.\n"
            "7. 가구유형이 '자녀와 함께 거주'여도 기초연금·장기요양·의료비 등은 어르신 단독 소득으로 판단하세요.\n"
            "반드시 JSON만 출력하고 다른 설명은 쓰지 마세요."
        )

    user_msg = f"""사용자 정보: {profile_lines}

복지서비스 목록:
{benefit_lines}

각 서비스에 대해 자격 여부를 분석하여 아래 JSON 형식으로 출력하세요.
status는 "가능", "불가", "확인필요" 중 하나, reason은 20자 이내:
{{"서비스명": {{"status": "가능", "reason": "이유"}}, ...}}"""

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user",   "content": user_msg},
        ],
        max_tokens=4000,
        temperature=0,
    )

    raw = response.choices[0].message.content or ""
    try:
        start = raw.find("{")
        end   = raw.rfind("}") + 1
        ai_results = json.loads(raw[start:end])
        final = {**pre_disqualified, **ai_results}
        _save_cache(key, final)
        return final
    except Exception:
        base = {b["name"]: {"status": "확인필요", "reason": "결과 파싱 오류"} for b in benefits_to_analyze}
        return {**pre_disqualified, **base}


def get_application_guide(benefit_name: str, user_profile: dict = None) -> str:
    profile_text = ""
    if user_profile:
        profile_text = (
            f"\n[신청인 정보]\n"
            f"나이: {user_profile.get('age')}세 / "
            f"가구유형: {user_profile.get('household','미입력')} / "
            f"월소득: {user_profile.get('income','미입력')} / "
            f"장애여부: {user_profile.get('disability','없음')}\n"
        )

    prompt = f"""'{benefit_name}' 혜택 신청 방법을 아래 구조로 안내해 주세요.
{profile_text}
어르신도 쉽게 따라할 수 있도록 쉬운 말로 작성해 주세요.

**📋 필요 서류**
- (서류 목록을 항목별로)

**📍 신청 방법 (단계별)**
1. (첫 번째 단계)
2. ...

**⏱ 처리 기간**
(신청 후 결과까지 걸리는 기간)

**⚠️ 꼭 확인하세요**
- (주의사항 또는 자주 하는 실수)

**📞 문의처**
(담당 기관 및 전화번호)"""

    return ask_claude(prompt)
