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


def get_application_guide(benefit_name: str) -> str:
    prompt = f"""'{benefit_name}' 혜택 신청 방법을 어르신도 따라할 수 있도록
번호를 붙여 단계별로 설명해주세요.
필요한 서류와 신청 장소(또는 사이트)도 포함해주세요."""

    return ask_claude(prompt)
