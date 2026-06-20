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

    benefit_lines = "\n".join(
        f"- {b['name']} ({b.get('income_level','전체')}, {b.get('age_min',0)}세이상)"
        for b in benefits
    )

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
        temperature=0.3,
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
