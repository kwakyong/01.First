WELFARE_BENEFITS = [
    {
        "id": 1,
        "name": "기초연금",
        "category": "노후소득",
        "description": "만 65세 이상 어르신 중 소득·재산이 적은 분께 매달 연금을 드립니다.",
        "age_min": 65,
        "income_level": "하위 70%",
        "amount": "월 최대 334,810원",
        "apply_where": "주민센터 또는 복지로(bokjiro.go.kr)",
    },
    {
        "id": 2,
        "name": "노인장기요양보험",
        "category": "돌봄서비스",
        "description": "혼자 일상생활이 어려운 어르신께 가정방문 돌봄 또는 시설 이용을 지원합니다.",
        "age_min": 65,
        "income_level": "전체",
        "amount": "등급별 월 한도액 지원",
        "apply_where": "국민건강보험공단 지사",
    },
    {
        "id": 3,
        "name": "노인 의료비 지원",
        "category": "의료",
        "description": "저소득 어르신의 의료비 본인부담금 일부를 지원합니다.",
        "age_min": 60,
        "income_level": "기준 중위소득 100% 이하",
        "amount": "연간 최대 120만원",
        "apply_where": "주민센터",
    },
    {
        "id": 4,
        "name": "노인 일자리 및 사회활동 지원",
        "category": "일자리",
        "description": "어르신이 활동적인 생활을 유지할 수 있도록 일자리와 사회 참여 기회를 제공합니다.",
        "age_min": 60,
        "income_level": "전체",
        "amount": "월 27만원~40만원 (활동비)",
        "apply_where": "읍·면·동 주민센터 또는 노인복지관",
    },
    {
        "id": 5,
        "name": "장애인 연금",
        "category": "장애지원",
        "description": "중증장애인 중 소득·재산이 적은 분께 매달 연금을 드립니다.",
        "age_min": 18,
        "income_level": "하위 70%",
        "amount": "월 최대 334,810원",
        "apply_where": "주민센터 또는 복지로(bokjiro.go.kr)",
    },
    {
        "id": 6,
        "name": "에너지바우처",
        "category": "생활지원",
        "description": "에너지 취약계층 어르신께 냉·난방비를 바우처로 지원합니다.",
        "age_min": 65,
        "income_level": "기준 중위소득 60% 이하",
        "amount": "연간 최대 643,400원",
        "apply_where": "주민센터",
    },
]

CATEGORIES = list({b["category"] for b in WELFARE_BENEFITS})


def get_benefits_by_age(age: int) -> list:
    return [b for b in WELFARE_BENEFITS if b["age_min"] <= age]


def get_benefits_by_category(category: str) -> list:
    if category == "전체":
        return WELFARE_BENEFITS
    return [b for b in WELFARE_BENEFITS if b["category"] == category]
