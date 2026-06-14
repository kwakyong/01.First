import os
import requests
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent
load_dotenv(BASE_DIR / ".env", override=True)
if not os.getenv("BOKJIRO_API_KEY"):
    load_dotenv(BASE_DIR / ".env.example", override=True)


def _get_api_key() -> str:
    try:
        import streamlit as st
        return st.secrets.get("BOKJIRO_API_KEY", os.getenv("BOKJIRO_API_KEY", ""))
    except Exception:
        return os.getenv("BOKJIRO_API_KEY", "")


BOKJIRO_URL = "https://api.odcloud.kr/api/15083323/v1/uddi:3929b807-3420-44d7-a851-cc741fce65a1"

REGIONS = ["전국공통", "서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종",
           "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"]

CENTRAL_MINISTRIES = [
    "보건복지부", "행정안전부", "고용노동부", "여성가족부", "국토교통부",
    "교육부", "문화체육관광부", "국가보훈", "기획재정부", "환경부",
    "농림축산식품부", "과학기술정보통신부", "산업통상자원부", "중소벤처기업부",
    "해양수산부", "금융위원회", "법무부", "통계청"
]

# 추천 서비스 (항상 상단 고정)
TOP_BENEFITS = [
    {
        "id": "top-1", "name": "기초연금", "category": "노후소득", "region": "전국공통",
        "description": "만 65세 이상 어르신 중 소득·재산이 적은 분께 매달 연금을 드립니다.",
        "age_min": 65, "income_level": "하위 70%",
        "amount": "월 최대 334,810원", "apply_where": "주민센터 또는 복지로", "url": "",
    },
    {
        "id": "top-2", "name": "노인장기요양보험", "category": "돌봄서비스", "region": "전국공통",
        "description": "혼자 일상생활이 어려운 어르신께 가정방문 돌봄 또는 시설 이용을 지원합니다.",
        "age_min": 65, "income_level": "전체",
        "amount": "등급별 월 한도액 지원", "apply_where": "국민건강보험공단 지사", "url": "",
    },
    {
        "id": "top-3", "name": "기초생활보장 생계급여", "category": "기초생활", "region": "전국공통",
        "description": "생활이 어려운 분들께 매달 생활비를 지원합니다.",
        "age_min": 0, "income_level": "기준 중위소득 32% 이하",
        "amount": "가구 규모별 차등 지급", "apply_where": "읍·면·동 주민센터", "url": "",
    },
    {
        "id": "top-4", "name": "에너지바우처", "category": "생활지원", "region": "전국공통",
        "description": "에너지 취약계층 어르신께 냉·난방비를 바우처로 지원합니다.",
        "age_min": 65, "income_level": "기준 중위소득 60% 이하",
        "amount": "연간 최대 643,400원", "apply_where": "주민센터", "url": "",
    },
    {
        "id": "top-5", "name": "노인 일자리 및 사회활동 지원", "category": "일자리", "region": "전국공통",
        "description": "어르신이 활동적인 생활을 유지할 수 있도록 일자리와 사회 참여 기회를 제공합니다.",
        "age_min": 60, "income_level": "전체",
        "amount": "월 27만원~40만원", "apply_where": "읍·면·동 주민센터 또는 노인복지관", "url": "",
    },
    {
        "id": "top-6", "name": "틀니·임플란트 건강보험 지원", "category": "의료", "region": "전국공통",
        "description": "만 65세 이상 어르신의 틀니 및 임플란트 비용 일부를 건강보험으로 지원합니다.",
        "age_min": 65, "income_level": "건강보험 가입자 전체",
        "amount": "본인부담률 30%", "apply_where": "치과 병·의원", "url": "",
    },
    {
        "id": "top-7", "name": "독거노인 응급안전 알림서비스", "category": "안전", "region": "전국공통",
        "description": "응급상황 발생 시 자동으로 감지해 119에 연결해 드리는 서비스입니다.",
        "age_min": 65, "income_level": "전체",
        "amount": "무료 (장비 설치)", "apply_where": "읍·면·동 주민센터", "url": "",
    },
    {
        "id": "top-8", "name": "노인 치매 치료관리비 지원", "category": "의료", "region": "전국공통",
        "description": "치매로 진단받은 어르신의 치료제 및 치료비를 지원합니다.",
        "age_min": 60, "income_level": "전국가구 평균소득 120% 이하",
        "amount": "월 최대 36만원", "apply_where": "치매안심센터", "url": "",
    },
    {
        "id": "top-9", "name": "경로우대 (교통·문화시설)", "category": "여가·문화", "region": "전국공통",
        "description": "지하철 무임 승차, 공원·고궁·박물관 무료 입장 등 다양한 혜택을 드립니다.",
        "age_min": 65, "income_level": "전체",
        "amount": "교통 무임 + 시설 무료/할인", "apply_where": "자동 적용 (신분증 제시)", "url": "",
    },
    {
        "id": "top-10", "name": "노인 주거 개보수 지원", "category": "주거", "region": "전국공통",
        "description": "저소득 어르신의 노후 주택 수선·개보수 비용을 지원합니다.",
        "age_min": 65, "income_level": "기준 중위소득 100% 이하",
        "amount": "최대 1,241만원", "apply_where": "읍·면·동 주민센터", "url": "",
    },
    {
        "id": "top-11", "name": "장애인 연금", "category": "장애지원", "region": "전국공통",
        "description": "중증장애인 중 소득·재산이 적은 분께 매달 연금을 드립니다.",
        "age_min": 18, "income_level": "하위 70%",
        "amount": "월 최대 334,810원", "apply_where": "주민센터", "url": "",
    },
    {
        "id": "top-12", "name": "노인 돌봄 기본서비스", "category": "돌봄서비스", "region": "전국공통",
        "description": "혼자 사시는 어르신 또는 노인 부부 가구에 안전 확인, 생활교육, 서비스 연계를 제공합니다.",
        "age_min": 65, "income_level": "전체",
        "amount": "무료", "apply_where": "읍·면·동 주민센터", "url": "",
    },
    {
        "id": "top-13", "name": "노인 안(眼)검진 및 개안수술 지원", "category": "의료", "region": "전국공통",
        "description": "저소득 어르신의 눈 검진과 백내장 등 개안수술 비용을 지원합니다.",
        "age_min": 60, "income_level": "기준 중위소득 60% 이하",
        "amount": "수술비 전액 지원", "apply_where": "읍·면·동 주민센터", "url": "",
    },
    {
        "id": "top-14", "name": "노인 복지관 운영", "category": "여가·문화", "region": "전국공통",
        "description": "어르신의 교양·취미·사회참여 활동 및 무료 식사를 제공합니다.",
        "age_min": 60, "income_level": "전체",
        "amount": "무료 또는 저렴한 이용료", "apply_where": "지역 노인복지관", "url": "",
    },
    {
        "id": "top-15", "name": "노인 의료비 지원", "category": "의료", "region": "전국공통",
        "description": "저소득 어르신의 의료비 본인부담금 일부를 지원합니다.",
        "age_min": 60, "income_level": "기준 중위소득 100% 이하",
        "amount": "연간 최대 120만원", "apply_where": "주민센터", "url": "",
    },
]

SAMPLE_BENEFITS = TOP_BENEFITS
CATEGORIES = sorted(set(b["category"] for b in TOP_BENEFITS))


def _detect_region(item: dict) -> str:
    text = item.get("소관부처명", "") + " " + item.get("소관조직명", "")
    if any(m in text for m in CENTRAL_MINISTRIES):
        return "전국공통"
    for region in REGIONS[1:]:  # 전국공통 제외
        if region in text:
            return region
    return "전국공통"


def fetch_welfare_benefits(call_type: str = "A") -> tuple:
    """복지로 API 전체 데이터 페이지네이션 로드."""
    api_key = _get_api_key()
    if not api_key:
        return TOP_BENEFITS, "⚠️ API 키 없음 → 추천 서비스만 표시 중"

    try:
        headers = {"Authorization": f"Infuser {api_key}"}
        all_items = []
        page = 1
        per_page = 100
        total = None

        while True:
            params = {"page": page, "perPage": per_page}
            resp = requests.get(BOKJIRO_URL, headers=headers, params=params, timeout=10)

            if resp.status_code == 401:
                return TOP_BENEFITS, "❌ 인증 실패 (401) → API 키를 확인하세요"
            if resp.status_code != 200:
                return TOP_BENEFITS, f"❌ API 오류 (HTTP {resp.status_code})"

            data = resp.json()
            if total is None:
                total = data.get("totalCount", 0)

            items = data.get("data", [])
            if not items:
                break

            all_items.extend(items)

            if len(all_items) >= total or len(items) < per_page:
                break

            page += 1

        if all_items:
            parsed = _parse_api_response(all_items)
            return parsed, f"✅ 복지로 API 연결 성공 (전체 {total}개 로드)"

        return TOP_BENEFITS, "⚠️ API 데이터 없음 → 추천 서비스만 표시 중"

    except Exception as e:
        return TOP_BENEFITS, f"❌ API 호출 오류: {str(e)}"


def _parse_api_response(items: list) -> list:
    result = []
    for i, item in enumerate(items, 1):
        url = item.get("서비스URL") or item.get("사이트", "")
        contact = item.get("대표문의", "")
        apply_where = contact if contact else "복지로(bokjiro.go.kr) 또는 주민센터"
        result.append({
            "id": item.get("서비스아이디", i),
            "name": item.get("서비스명", f"서비스 {i}"),
            "category": item.get("소관부처명", "기타"),
            "region": _detect_region(item),
            "description": item.get("서비스요약", ""),
            "age_min": 0,
            "income_level": "전체",
            "amount": "상세 내용은 서비스 페이지 확인",
            "apply_where": apply_where,
            "url": url,
        })
    return result


def get_benefits_by_category(category: str) -> tuple:
    benefits, debug = fetch_welfare_benefits()
    if category == "전체":
        return benefits, debug
    return [b for b in benefits if b["category"] == category], debug


def get_benefits_by_region(region: str) -> tuple:
    benefits, debug = fetch_welfare_benefits()
    if region == "전국공통":
        return [b for b in benefits if b.get("region", "전국공통") == "전국공통"], debug
    # 선택 지역 + 전국공통 함께 표시
    return [b for b in benefits if b.get("region") in ("전국공통", region)], debug


def get_benefits_by_age(age: int) -> list:
    benefits, _ = fetch_welfare_benefits()
    return [b for b in benefits if b["age_min"] <= age]
