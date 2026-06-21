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
        "required_health": ["치매 진단 또는 의심"],
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
    # ── 확장 항목 (16~40) ──────────────────────────────
    {
        "id": "top-16", "name": "기초생활보장 의료급여", "category": "기초생활", "region": "전국공통",
        "description": "기초생활수급자에게 의료비를 국가가 대부분 부담하여 병원 이용 부담을 최소화합니다.",
        "age_min": 0, "income_level": "기준 중위소득 40% 이하",
        "amount": "의료비 대부분 국가 부담", "apply_where": "읍·면·동 주민센터", "url": "",
    },
    {
        "id": "top-17", "name": "기초생활보장 주거급여", "category": "주거", "region": "전국공통",
        "description": "저소득 가구의 임차료 또는 자가 주택 수선비를 지원합니다.",
        "age_min": 0, "income_level": "기준 중위소득 48% 이하",
        "amount": "지역·가구 규모별 차등 지급", "apply_where": "읍·면·동 주민센터", "url": "",
    },
    {
        "id": "top-18", "name": "긴급복지지원", "category": "생활지원", "region": "전국공통",
        "description": "갑작스러운 위기 상황(실직·질병·사망 등)에 처한 가구에 즉각적인 생계·의료·주거 지원을 제공합니다.",
        "age_min": 0, "income_level": "기준 중위소득 75% 이하 (위기상황)",
        "amount": "생계 최대 162만원, 의료 300만원 이내", "apply_where": "읍·면·동 주민센터 또는 복지로", "url": "",
    },
    {
        "id": "top-19", "name": "차상위계층 의료비 지원", "category": "의료", "region": "전국공통",
        "description": "차상위계층에게 본인부담 의료비 일부를 지원합니다.",
        "age_min": 0, "income_level": "기준 중위소득 50% 이하",
        "amount": "본인부담금 지원", "apply_where": "읍·면·동 주민센터", "url": "",
    },
    {
        "id": "top-20", "name": "노인 건강검진 (암검진 포함)", "category": "의료", "region": "전국공통",
        "description": "일반건강검진과 위암·대장암·간암·유방암·자궁경부암 등 5대 암 검진을 무료 또는 저렴하게 받을 수 있습니다.",
        "age_min": 40, "income_level": "건강보험 가입자 전체",
        "amount": "무료~본인부담 10%", "apply_where": "국민건강보험 지정 의료기관", "url": "",
    },
    {
        "id": "top-21", "name": "보건소 방문건강관리 서비스", "category": "의료", "region": "전국공통",
        "description": "거동이 불편하거나 만성질환을 가진 어르신 가정을 보건소 간호사가 직접 방문하여 건강관리를 도와드립니다.",
        "age_min": 65, "income_level": "전체 (취약계층·만성질환자 우선 배정)",
        "amount": "무료", "apply_where": "지역 보건소", "url": "",
    },
    {
        "id": "top-22", "name": "치매안심센터 서비스", "category": "의료", "region": "전국공통",
        "description": "치매 조기검진, 환자 등록·관리, 치매쉼터 이용, 가족 교육 등 치매 관련 통합 서비스를 제공합니다.",
        "age_min": 60, "income_level": "전체",
        "amount": "무료", "apply_where": "치매안심센터 (시·군·구 보건소 내)", "url": "",
    },
    {
        "id": "top-23", "name": "재난적 의료비 지원", "category": "의료", "region": "전국공통",
        "description": "과도한 의료비 부담으로 생계가 어려운 환자에게 의료비를 지원합니다.",
        "age_min": 0, "income_level": "기준 중위소득 200% 이하",
        "amount": "연간 최대 3,000만원", "apply_where": "국민건강보험공단 지사", "url": "",
    },
    {
        "id": "top-24", "name": "노인 무릎 인공관절 수술 지원", "category": "의료", "region": "전국공통",
        "description": "저소득 노인의 무릎 인공관절 수술 비용을 지원합니다.",
        "age_min": 60, "income_level": "기준 중위소득 60% 이하",
        "amount": "수술비 120만원 이내", "apply_where": "읍·면·동 주민센터", "url": "",
    },
    {
        "id": "top-25", "name": "노인 불소도포·스케일링 지원", "category": "의료", "region": "전국공통",
        "description": "어르신의 구강 건강을 위해 불소도포와 스케일링을 건강보험으로 지원합니다.",
        "age_min": 65, "income_level": "건강보험 가입자 전체",
        "amount": "연 1회 급여 적용", "apply_where": "치과 병·의원", "url": "",
    },
    {
        "id": "top-26", "name": "노인맞춤돌봄서비스", "category": "돌봄서비스", "region": "전국공통",
        "description": "신체·인지기능이 저하된 어르신에게 안전지원·사회참여·생활교육·일상생활지원 등 맞춤형 서비스를 제공합니다.",
        "age_min": 65, "income_level": "전체 (독거·고령부부 우선)",
        "amount": "무료", "apply_where": "읍·면·동 주민센터", "url": "",
    },
    {
        "id": "top-27", "name": "재가 장기요양서비스 (방문요양·목욕)", "category": "돌봄서비스", "region": "전국공통",
        "description": "장기요양 1~5등급 판정 어르신 가정에 요양보호사가 방문하여 신체활동·가사·목욕을 지원합니다.",
        "age_min": 65, "income_level": "전체 (본인부담 15%)",
        "amount": "등급별 월 한도액 내 지원", "apply_where": "국민건강보험공단 → 재가장기요양기관", "url": "",
    },
    {
        "id": "top-28", "name": "노인요양시설 입소 지원", "category": "돌봄서비스", "region": "전국공통",
        "description": "혼자 생활이 어려운 어르신이 요양원 또는 노인요양공동생활가정에 입소하여 24시간 돌봄을 받을 수 있습니다.",
        "age_min": 65, "income_level": "전체 (본인부담 20%)",
        "amount": "등급별 입소비 지원", "apply_where": "국민건강보험공단 지사", "url": "",
    },
    {
        "id": "top-29", "name": "노인보호전문기관 (노인학대 예방)", "category": "안전", "region": "전국공통",
        "description": "노인 학대 예방 및 피해 어르신 보호·지원 서비스를 제공합니다. 24시간 신고 전화를 운영합니다.",
        "age_min": 60, "income_level": "전체",
        "amount": "무료 (신고전화 1577-1389)", "apply_where": "노인보호전문기관 또는 112·119 신고", "url": "",
    },
    {
        "id": "top-30", "name": "스마트홈 IoT 안전관리 서비스", "category": "안전", "region": "전국공통",
        "description": "독거노인 가정에 IoT 센서를 설치하여 활동 감지, 이상 행동 알림, 생활지원을 제공합니다.",
        "age_min": 65, "income_level": "전체 (독거노인 대상, 취약계층 우선 배정)",
        "amount": "무료 (장비 및 서비스)", "apply_where": "읍·면·동 주민센터", "url": "",
    },
    {
        "id": "top-31", "name": "주거급여 (임차가구 임대료 지원)", "category": "주거", "region": "전국공통",
        "description": "저소득 임차 가구에 지역·가구원 수에 따라 임차료를 매월 지원합니다.",
        "age_min": 0, "income_level": "기준 중위소득 48% 이하",
        "amount": "지역별 월 최대 34만원 (1인 기준)", "apply_where": "읍·면·동 주민센터", "url": "",
    },
    {
        "id": "top-32", "name": "공공실버주택 공급", "category": "주거", "region": "전국공통",
        "description": "저소득 고령자에게 복지서비스가 연계된 공공임대주택을 저렴하게 공급합니다.",
        "age_min": 65, "income_level": "소득·자산 기준 충족",
        "amount": "시세 30~50% 임대료", "apply_where": "LH 마이홈 (1600-1004)", "url": "",
    },
    {
        "id": "top-33", "name": "장애인 활동지원서비스", "category": "장애지원", "region": "전국공통",
        "description": "장애로 혼자 일상생활이 어려운 분께 신체활동, 가사활동, 외출 동행 등을 지원합니다.",
        "age_min": 6, "income_level": "전체 (소득에 따라 본인부담 차등)",
        "amount": "월 최대 480시간 지원", "apply_where": "읍·면·동 주민센터", "url": "",
    },
    {
        "id": "top-34", "name": "장애인 보조기기 교부", "category": "장애지원", "region": "전국공통",
        "description": "저소득 장애인에게 욕창예방방석, 음성시계, 보청기 등 보조기기를 무료로 제공합니다.",
        "age_min": 0, "income_level": "기준 중위소득 100% 이하",
        "amount": "품목별 실비 지원", "apply_where": "읍·면·동 주민센터", "url": "",
    },
    {
        "id": "top-35", "name": "장애수당", "category": "장애지원", "region": "전국공통",
        "description": "등록 장애인 중 기초생활수급자 또는 차상위계층에게 매달 장애수당을 지급합니다.",
        "age_min": 18, "income_level": "기준 중위소득 50% 이하",
        "amount": "월 6만원~30만원", "apply_where": "읍·면·동 주민센터", "url": "",
    },
    {
        "id": "top-36", "name": "시니어 인턴십", "category": "일자리", "region": "전국공통",
        "description": "만 60세 이상 구직자가 기업에 인턴으로 취업할 수 있도록 연결하고 정규직 전환을 지원합니다.",
        "age_min": 60, "income_level": "전체",
        "amount": "인건비 지원 (기업 통해 지급)", "apply_where": "고용복지플러스센터 또는 한국노인인력개발원", "url": "",
    },
    {
        "id": "top-37", "name": "고령자 계속고용장려금", "category": "일자리", "region": "전국공통",
        "description": "정년이 지난 60세 이상 근로자를 계속 고용하는 기업을 지원하여 어르신의 일자리를 유지해 드립니다.",
        "age_min": 60, "income_level": "전체",
        "amount": "분기당 최대 90만원 (근로자 1인)", "apply_where": "고용복지플러스센터", "url": "",
    },
    {
        "id": "top-38", "name": "문화누리카드", "category": "여가·문화", "region": "전국공통",
        "description": "기초생활수급자 및 차상위계층에게 문화·여행·체육 활동을 즐길 수 있는 지원카드를 드립니다.",
        "age_min": 6, "income_level": "기초생활수급자·차상위계층",
        "amount": "연간 13만원", "apply_where": "문화누리 누리집 또는 주민센터", "url": "",
    },
    {
        "id": "top-39", "name": "노인 평생교육 프로그램", "category": "여가·문화", "region": "전국공통",
        "description": "어르신의 스마트폰 활용, 외국어, 공예, 건강체조 등 다양한 평생교육 프로그램을 운영합니다.",
        "age_min": 60, "income_level": "전체",
        "amount": "무료 또는 저렴한 수강료", "apply_where": "노인복지관·평생학습관", "url": "",
    },
    {
        "id": "top-40", "name": "노인 결식 우려자 급식 지원", "category": "생활지원", "region": "전국공통",
        "description": "결식 우려가 있는 어르신에게 경로식당 무료급식, 도시락 배달, 밑반찬 배달 서비스를 제공합니다.",
        "age_min": 60, "income_level": "전체 (소득 무관, 저소득·독거 우선 배정)",
        "amount": "무료 (1일 1식 이상)", "apply_where": "읍·면·동 주민센터", "url": "",
    },
    {
        "id": "top-41", "name": "양곡할인 (정부양곡 할인 공급)", "category": "생활지원", "region": "전국공통",
        "description": "정부양곡(쌀)을 기초수급가구 및 차상위계층에 시중가 대비 20% 할인 공급합니다.",
        "age_min": 0, "income_level": "기준 중위소득 50% 이하 (차상위계층 이하)",
        "amount": "시중가 대비 약 20% 할인", "apply_where": "읍·면·동 주민센터", "url": "",
    },
    {
        "id": "top-42", "name": "건강보험 본인부담상한제", "category": "의료", "region": "전국공통",
        "description": "연간 의료비 본인부담이 소득 수준별 상한액 초과 시 건강보험공단이 초과분을 자동 환급합니다.",
        "age_min": 0, "income_level": "건강보험 가입자 전체 (소득별 상한액 차등)",
        "amount": "초과 의료비 전액 환급", "apply_where": "국민건강보험공단 (자동 지급)", "url": "",
    },
    {
        "id": "top-43", "name": "노인 정신건강 지원 (우울증·자살예방)", "category": "의료", "region": "전국공통",
        "description": "60세 이상 어르신의 우울증 선별검사, 심리상담, 자살예방 프로그램을 보건소에서 무료 제공합니다.",
        "age_min": 60, "income_level": "전체",
        "amount": "무료", "apply_where": "지역 보건소 또는 정신건강복지센터", "url": "",
    },
    {
        "id": "top-44", "name": "노인 가사간병 방문지원", "category": "돌봄서비스", "region": "전국공통",
        "description": "저소득 어르신 가정에 가사·간병 서비스 인력을 파견하여 일상생활을 지원합니다.",
        "age_min": 65, "income_level": "기준 중위소득 70% 이하",
        "amount": "월 24시간 이내 (일부 본인부담)", "apply_where": "읍·면·동 주민센터", "url": "",
    },
    {
        "id": "top-45", "name": "어르신 독감·폐렴구균 예방접종 (무료)", "category": "의료", "region": "전국공통",
        "description": "만 65세 이상 어르신께 독감(인플루엔자) 및 폐렴구균 예방접종을 매년 무료로 제공합니다.",
        "age_min": 65, "income_level": "전체 (65세 이상 누구나)",
        "amount": "무료", "apply_where": "지역 보건소 또는 지정 의료기관", "url": "",
    },
]

# 사용자 친화적 카테고리 목록 (드롭다운용)
USER_CATEGORIES = [
    "노후·연금", "의료·건강", "돌봄·요양", "생활지원",
    "일자리·창업", "주거", "장애지원", "안전·긴급", "여가·문화",
]

# TOP_BENEFITS 카테고리 → USER_CATEGORIES 매핑
TOP_TO_USER_CAT = {
    "노후소득": "노후·연금",
    "의료":     "의료·건강",
    "돌봄서비스": "돌봄·요양",
    "생활지원": "생활지원",
    "기초생활": "생활지원",
    "일자리":   "일자리·창업",
    "주거":     "주거",
    "장애지원": "장애지원",
    "안전":     "안전·긴급",
    "여가·문화": "여가·문화",
}

# API 서비스명/내용 키워드 → USER_CATEGORIES 매핑
_KEYWORD_CATEGORY = [
    ("노후·연금",   ["연금", "노령", "기초연금", "노후소득"]),
    ("의료·건강",   ["의료", "건강", "치료", "병원", "보건", "간호", "재활", "검진",
                    "틀니", "임플란트", "치매", "안과", "한방", "약제", "수술", "진료"]),
    ("돌봄·요양",   ["돌봄", "요양", "방문", "재가", "장기요양", "케어", "간병"]),
    ("생활지원",    ["생계", "생활비", "식품", "급식", "에너지", "난방", "냉방",
                    "바우처", "기초생활", "긴급복지", "이동지원"]),
    ("일자리·창업", ["일자리", "취업", "고용", "직업훈련", "창업", "근로", "직무"]),
    ("주거",        ["주거", "주택", "임대", "전세", "개보수", "수선", "집수리"]),
    ("장애지원",    ["장애", "보조기기", "발달장애", "장애인"]),
    ("안전·긴급",   ["안전", "긴급", "재난", "응급", "위기", "알림서비스", "감지"]),
    ("여가·문화",   ["여가", "문화", "체육", "스포츠", "관광", "교양", "취미", "복지관", "경로"]),
]

SAMPLE_BENEFITS = TOP_BENEFITS
CATEGORIES = sorted(set(b["category"] for b in TOP_BENEFITS))


def _get_user_category(name: str, desc: str) -> str:
    text = (name + " " + desc).lower()
    for cat, keywords in _KEYWORD_CATEGORY:
        if any(kw in text for kw in keywords):
            return cat
    return "기타"


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
        name = item.get("서비스명", f"서비스 {i}")
        desc = item.get("서비스요약", "")
        result.append({
            "id": item.get("서비스아이디", i),
            "name": name,
            "category": item.get("소관부처명", "기타"),
            "user_category": _get_user_category(name, desc),
            "region": _detect_region(item),
            "description": desc,
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


# ────────────────────────────────────────────────────────────
# 청소년·대학생 복지 (만 15~24세)
# ────────────────────────────────────────────────────────────

YOUTH_CATEGORIES = [
    "학비·장학금", "생활비지원", "주거", "일자리·취업",
    "건강·심리", "문화·여가", "자립지원", "창업·금융",
]

TOP_YOUTH_BENEFITS = [
    # 학비·장학금
    {
        "id": "youth-1", "name": "국가장학금 I유형", "category": "학비·장학금", "region": "전국공통",
        "description": "소득분위 8구간 이하 대학생에게 등록금을 지원합니다. 학자금 지원 8구간 이하 재학생 대상.",
        "age_min": 18, "age_max": 35, "income_level": "소득분위 1~8구간",
        "amount": "연간 최대 570만원", "apply_where": "한국장학재단 (www.kosaf.go.kr)", "url": "",
    },
    {
        "id": "youth-2", "name": "국가장학금 II유형", "category": "학비·장학금", "region": "전국공통",
        "description": "대학과 연계하여 저소득층 학생에게 등록금을 추가 지원합니다.",
        "age_min": 18, "age_max": 35, "income_level": "소득분위 1~9구간",
        "amount": "대학별 차등 지원", "apply_where": "한국장학재단 (www.kosaf.go.kr)", "url": "",
    },
    {
        "id": "youth-3", "name": "근로장학금", "category": "학비·장학금", "region": "전국공통",
        "description": "저소득 대학생이 교내·외에서 근로하고 장학금을 받는 제도입니다.",
        "age_min": 18, "age_max": 35, "income_level": "소득분위 1~9구간",
        "amount": "시간당 9,860원 (월 최대 60시간)", "apply_where": "한국장학재단 (www.kosaf.go.kr)", "url": "",
    },
    {
        "id": "youth-4", "name": "취업 후 상환 학자금 대출", "category": "학비·장학금", "region": "전국공통",
        "description": "졸업 후 취업하여 소득이 생긴 뒤에 상환하는 대학 등록금 대출입니다.",
        "age_min": 18, "age_max": 35, "income_level": "소득분위 1~8구간",
        "amount": "등록금 전액 (연 1.7% 고정금리)", "apply_where": "한국장학재단 (www.kosaf.go.kr)", "url": "",
    },
    {
        "id": "youth-5", "name": "교육급여 (고등학생 학습지원비)", "category": "학비·장학금", "region": "전국공통",
        "description": "기초생활수급자 고등학생에게 학용품·교재비 등 학습활동을 위한 비용을 지원합니다.",
        "age_min": 15, "age_max": 18, "income_level": "기준 중위소득 50% 이하",
        "amount": "연 65만원", "apply_where": "읍·면·동 주민센터", "url": "",
    },
    # 생활비지원
    {
        "id": "youth-6", "name": "생활비 대출 (일반 상환)", "category": "생활비지원", "region": "전국공통",
        "description": "재학 중 생활비 부담을 줄이기 위한 저금리 학자금 생활비 대출입니다.",
        "age_min": 18, "age_max": 35, "income_level": "소득분위 1~9구간",
        "amount": "학기당 최대 150만원 (연 1.7~2.9%)", "apply_where": "한국장학재단 (www.kosaf.go.kr)", "url": "",
    },
    {
        "id": "youth-7", "name": "청년내일저축계좌", "category": "생활비지원", "region": "전국공통",
        "description": "저소득 청년이 매달 10만원을 저축하면 정부가 최대 30만원을 추가 지원합니다.",
        "age_min": 19, "age_max": 34, "income_level": "기준 중위소득 100% 이하",
        "amount": "월 최대 40만원 (본인 10 + 정부 30)", "apply_where": "복지로 또는 주민센터", "url": "",
    },
    {
        "id": "youth-8", "name": "방과후학교 자유수강권", "category": "생활비지원", "region": "전국공통",
        "description": "저소득층 학생이 방과후학교 프로그램을 무료로 수강할 수 있도록 바우처를 지원합니다.",
        "age_min": 15, "age_max": 18, "income_level": "기초생활수급자·차상위계층",
        "amount": "연 60만원 이내", "apply_where": "재학 중인 학교", "url": "",
    },
    {
        "id": "youth-9", "name": "문화누리카드 (청소년)", "category": "생활비지원", "region": "전국공통",
        "description": "기초생활수급자 및 차상위계층 청소년에게 문화·여행·체육 활동 지원카드를 드립니다.",
        "age_min": 6, "age_max": 24, "income_level": "기초생활수급자·차상위계층",
        "amount": "연 13만원", "apply_where": "문화누리 누리집 또는 주민센터", "url": "",
    },
    # 주거
    {
        "id": "youth-10", "name": "청년 월세 한시 특별지원", "category": "주거", "region": "전국공통",
        "description": "부모와 독립하여 거주하는 저소득 청년에게 월세를 최대 12개월 지원합니다.",
        "age_min": 19, "age_max": 34, "income_level": "기준 중위소득 60% 이하",
        "amount": "월 최대 20만원 (12개월)", "apply_where": "복지로 또는 주민센터", "url": "",
    },
    {
        "id": "youth-11", "name": "청년 전세임대주택", "category": "주거", "region": "전국공통",
        "description": "LH가 전세 주택을 계약하여 저소득 청년에게 저렴하게 재임대하는 주거 지원 제도입니다.",
        "age_min": 18, "age_max": 39, "income_level": "소득분위 1~4구간",
        "amount": "전세금의 1~2% 저렴하게 임대", "apply_where": "LH 마이홈 (1600-1004)", "url": "",
    },
    # 일자리·취업
    {
        "id": "youth-12", "name": "국민취업지원제도 (청년 I 유형)", "category": "일자리·취업", "region": "전국공통",
        "description": "취업에 어려움을 겪는 청년에게 취업지원서비스와 구직촉진수당을 제공합니다.",
        "age_min": 15, "age_max": 34, "income_level": "기준 중위소득 60% 이하",
        "amount": "월 50만원 (최대 6개월)", "apply_where": "고용복지플러스센터 또는 워크넷", "url": "",
    },
    {
        "id": "youth-13", "name": "청년 일경험 지원사업", "category": "일자리·취업", "region": "전국공통",
        "description": "미취업 청년이 기업에서 실무 경험을 쌓을 수 있도록 참여 기회를 제공하고 수당을 지급합니다.",
        "age_min": 18, "age_max": 34, "income_level": "전체",
        "amount": "월 최저임금 이상 (프로그램별 상이)", "apply_where": "워크넷 또는 고용복지플러스센터", "url": "",
    },
    {
        "id": "youth-14", "name": "청년 직업훈련 (내일배움카드)", "category": "일자리·취업", "region": "전국공통",
        "description": "취업 준비 청년에게 직업훈련비용을 지원하는 카드를 발급합니다.",
        "age_min": 15, "age_max": 34, "income_level": "전체",
        "amount": "5년간 최대 500만원", "apply_where": "고용복지플러스센터 또는 HRD-Net", "url": "",
    },
    {
        "id": "youth-15", "name": "고졸 취업 지원 (중소기업 취업연계)", "category": "일자리·취업", "region": "전국공통",
        "description": "고등학교 졸업 예정자·졸업자가 중소기업에 취업할 수 있도록 연계하고 장려금을 지원합니다.",
        "age_min": 15, "age_max": 24, "income_level": "전체",
        "amount": "취업성공 시 장려금 최대 200만원", "apply_where": "워크넷 또는 고용복지플러스센터", "url": "",
    },
    # 건강·심리
    {
        "id": "youth-16", "name": "청소년 건강검진", "category": "건강·심리", "region": "전국공통",
        "description": "고등학교 1학년(만 16세)에게 무료 건강검진을 실시합니다.",
        "age_min": 16, "age_max": 16, "income_level": "전체",
        "amount": "무료", "apply_where": "지정 검진기관 (학교 안내)", "url": "",
    },
    {
        "id": "youth-17", "name": "청년 마음건강 지원 (마음이음)", "category": "건강·심리", "region": "전국공통",
        "description": "정신건강에 어려움을 겪는 청년에게 심리상담 바우처를 지원합니다.",
        "age_min": 19, "age_max": 34, "income_level": "기준 중위소득 100% 이하",
        "amount": "1인당 최대 40만원 (10회 상담)", "apply_where": "정신건강복지센터 또는 복지로", "url": "",
    },
    {
        "id": "youth-18", "name": "청소년 위기상담 (청소년전화 1388)", "category": "건강·심리", "region": "전국공통",
        "description": "학교폭력, 가출, 자해 등 위기 청소년에게 24시간 전화·문자 상담 및 긴급지원을 제공합니다.",
        "age_min": 9, "age_max": 24, "income_level": "전체",
        "amount": "무료 (24시간 1388)", "apply_where": "전화 1388 또는 청소년상담복지센터", "url": "",
    },
    # 문화·여가
    {
        "id": "youth-19", "name": "청소년 문화패스 (만 15세)", "category": "문화·여가", "region": "전국공통",
        "description": "만 15세 청소년에게만 공연·전시·스포츠 등 문화 활동비를 지원합니다. 만 15세 전용.",
        "age_min": 15, "age_max": 15, "income_level": "전체",
        "amount": "연 10만원", "apply_where": "문화포털 또는 지역 문화원", "url": "",
    },
    {
        "id": "youth-19b", "name": "청년문화예술패스 (만 19~20세)", "category": "문화·여가", "region": "전국공통",
        "description": "만 19~20세(2006~2007년생) 청년 누구나 소득에 관계없이 공연·전시 관람비를 지원합니다.",
        "age_min": 19, "age_max": 20, "income_level": "전체 (소득 무관)",
        "amount": "연 15~20만원", "apply_where": "문화포털(culture.go.kr) 또는 누리집 신청", "url": "",
    },
    {
        "id": "youth-19c", "name": "서울청년문화패스 (만 21~23세, 서울)", "category": "문화·여가", "region": "서울",
        "description": "서울 거주 만 21~23세 청년(건강보험료 기준 중위소득 150% 이하)에게 문화 관람비를 지원합니다.",
        "age_min": 21, "age_max": 23, "income_level": "중위소득 150% 이하",
        "amount": "연 20만원", "apply_where": "서울청년포털(youth.seoul.go.kr)", "url": "",
    },
    {
        "id": "youth-19d", "name": "경기컬처패스 (경기도)", "category": "문화·여가", "region": "경기",
        "description": "경기도민 만 7세 이상 대상으로 문화·공연·전시 관람을 위한 문화소비쿠폰을 지급합니다.",
        "age_min": 7, "age_max": 24, "income_level": "전체",
        "amount": "연 최대 6만원", "apply_where": "경기문화재단 또는 토스뱅크 앱", "url": "",
    },
    {
        "id": "youth-20", "name": "청소년 수련활동 지원", "category": "문화·여가", "region": "전국공통",
        "description": "청소년수련관·청소년문화의집 등에서 다양한 동아리·체험 활동 프로그램을 저렴하게 이용할 수 있습니다.",
        "age_min": 9, "age_max": 24, "income_level": "전체",
        "amount": "무료 또는 저렴한 수강료", "apply_where": "지역 청소년수련관·문화의집", "url": "",
    },
    # 자립지원
    {
        "id": "youth-21", "name": "자립준비청년 자립수당", "category": "자립지원", "region": "전국공통",
        "description": "아동양육시설·공동생활가정 등에서 퇴소한 청년에게 자립 정착을 위한 수당을 지급합니다.",
        "age_min": 18, "age_max": 24, "income_level": "전체",
        "amount": "월 40만원 (최대 3년)", "apply_where": "읍·면·동 주민센터", "url": "",
    },
    {
        "id": "youth-22", "name": "자립준비청년 초기 정착금", "category": "자립지원", "region": "전국공통",
        "description": "보호종료 시 자립 생활에 필요한 초기 정착 비용을 일시 지원합니다.",
        "age_min": 18, "age_max": 18, "income_level": "전체",
        "amount": "500~1,000만원 (지역별 상이)", "apply_where": "아동보호기관 또는 주민센터", "url": "",
    },
    {
        "id": "youth-23", "name": "드림스타트 (취약 아동·청소년 통합지원)", "category": "자립지원", "region": "전국공통",
        "description": "취약가정 아동·청소년의 건강·교육·복지를 통합 지원하여 공정한 출발을 보장합니다.",
        "age_min": 0, "age_max": 12, "income_level": "기초생활수급자·차상위계층 등",
        "amount": "개별 서비스 연계 (무료)", "apply_where": "읍·면·동 주민센터 또는 드림스타트센터", "url": "",
    },
    # 창업·금융
    {
        "id": "youth-24", "name": "청년도약계좌", "category": "창업·금융", "region": "전국공통",
        "description": "청년이 매달 40~70만원을 저축하면 정부기여금과 비과세 혜택으로 5년 후 목돈을 마련할 수 있습니다.",
        "age_min": 19, "age_max": 34, "income_level": "개인소득 7,500만원 이하",
        "amount": "5년 만기 최대 5,000만원", "apply_where": "은행 앱 (국민·신한·농협·우리·하나 등)", "url": "",
    },
    {
        "id": "youth-25", "name": "청년 창업 지원 (창업진흥원)", "category": "창업·금융", "region": "전국공통",
        "description": "아이디어가 있는 청년에게 창업 공간, 자금, 멘토링을 지원하여 사업 시작을 돕습니다.",
        "age_min": 18, "age_max": 39, "income_level": "전체",
        "amount": "최대 1억원 (과제별 상이)", "apply_where": "창업진흥원 K-Startup (www.k-startup.go.kr)", "url": "",
    },
]

# TOP_YOUTH_BENEFITS category → YOUTH_CATEGORIES 매핑
YOUTH_TO_USER_CAT = {
    "학비·장학금": "학비·장학금",
    "생활비지원": "생활비지원",
    "주거": "주거",
    "일자리·취업": "일자리·취업",
    "건강·심리": "건강·심리",
    "문화·여가": "문화·여가",
    "자립지원": "자립지원",
    "창업·금융": "창업·금융",
}

# API 키워드 → 청소년 카테고리
_YOUTH_KEYWORD_CATEGORY = [
    ("학비·장학금",  ["장학금", "학자금", "등록금", "교육급여", "수강권", "학습지원"]),
    ("생활비지원",   ["생활비", "청년저축", "바우처", "급식", "생계", "긴급지원"]),
    ("주거",         ["월세", "전세임대", "주거", "주택", "기숙사"]),
    ("일자리·취업",  ["취업", "일자리", "인턴", "직업훈련", "훈련카드", "구직", "고졸"]),
    ("건강·심리",    ["건강검진", "심리상담", "정신건강", "마음건강", "위기상담"]),
    ("문화·여가",    ["문화패스", "수련", "동아리", "여가", "체험", "문화활동"]),
    ("자립지원",     ["자립", "보호종료", "드림스타트", "위탁"]),
    ("창업·금융",    ["청년도약", "창업", "저축계좌", "금융"]),
]


def _get_youth_user_category(name: str, desc: str) -> str:
    text = (name + " " + desc).lower()
    for cat, keywords in _YOUTH_KEYWORD_CATEGORY:
        if any(kw in text for kw in keywords):
            return cat
    return "기타"


_YOUTH_KEYWORDS = [
    "청소년", "청년", "대학생", "고등학생", "학자금", "장학금",
    "등록금", "수강권", "드림스타트", "자립준비", "보호종료",
    "청년도약", "청년저축", "일경험", "고졸취업",
]


def get_youth_benefits_by_region(region: str) -> tuple:
    """API 367개 중 청소년·청년 키워드 항목 필터링 + TOP_YOUTH_BENEFITS 합산."""
    benefits, debug = fetch_welfare_benefits()

    api_youth = []
    for b in benefits:
        text = b["name"] + " " + b.get("description", "")
        if any(kw in text for kw in _YOUTH_KEYWORDS):
            b = dict(b)
            b["user_category"] = _get_youth_user_category(b["name"], b.get("description", ""))
            api_youth.append(b)

    if region != "전국공통":
        api_youth = [b for b in api_youth if b.get("region") in ("전국공통", region)]

    return api_youth, debug
