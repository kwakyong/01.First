import os
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
    """
    import json

    def _age_range(b):
        mn = b.get("age_min", 0)
        mx = b.get("age_max")
        return f"{mn}~{mx}세" if mx else f"{mn}세 이상"

    benefit_lines = "\n".join(
        f"- {b['name']} | 나이:{_age_range(b)} | 소득:{b.get('income_level','전체')} | {b.get('description','')[:40]}"
        for b in benefits
    )

    # 청소년 프로필 여부 감지 (school_status 필드 존재 시)
    is_youth = "school_status" in user_profile

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
    else:
        profile_lines = (
            f"나이: {user_profile.get('age')}세 / "
            f"성별: {user_profile.get('gender','미입력')} / "
            f"가구유형: {user_profile.get('household','미입력')} / "
            f"가구원수: {user_profile.get('household_size','미입력')} / "
            f"월소득: {user_profile.get('income','미입력')} / "
            f"주택소유: {user_profile.get('home_ownership','미입력')} / "
            f"재산규모: {user_profile.get('asset_level','미입력')} / "
            f"장애여부: {user_profile.get('disability','없음')} / "
            f"건강상태: {user_profile.get('health_condition','없음')} / "
            f"본인사업자: {user_profile.get('own_business','없음')} / "
            f"배우자사업자: {user_profile.get('spouse_business','없음')} / "
            f"국가유공자: {user_profile.get('veteran','없음')} / "
            f"기타: {user_profile.get('notes','없음')}"
        )

    if is_youth:
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
        system_msg = (
            "당신은 대한민국 복지 자격 분석 전문가입니다. "
            "사용자 정보를 바탕으로 각 복지서비스 자격 여부를 판단합니다. "
            "나이·소득 기준을 충족할 가능성이 있으면 '가능' 또는 '확인필요'로 판단하고, "
            "명백히 기준 미달인 경우에만 '불가'로 판단하세요. "
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
        return json.loads(raw[start:end])
    except Exception:
        return {b["name"]: {"status": "확인필요", "reason": "결과 파싱 오류"} for b in benefits}


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
