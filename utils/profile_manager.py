import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
PROFILE_FILE      = DATA_DIR / "user_profile.json"
ELIGIBILITY_FILE  = DATA_DIR / "eligibility_results.json"
BOOKMARK_FILE     = DATA_DIR / "bookmarks.json"


def save_profile(profile: dict) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)


def load_profile() -> dict:
    if PROFILE_FILE.exists():
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def delete_profile() -> None:
    if PROFILE_FILE.exists():
        PROFILE_FILE.unlink()


def save_eligibility_results(results: dict) -> None:
    """자격확인 AI 분석 결과 저장."""
    DATA_DIR.mkdir(exist_ok=True)
    with open(ELIGIBILITY_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


def load_eligibility_results() -> dict:
    """저장된 자격확인 결과 로드. 없으면 빈 dict."""
    if ELIGIBILITY_FILE.exists():
        with open(ELIGIBILITY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def load_bookmarks() -> dict:
    """북마크 로드. {서비스명: "관심"|"신청예정"|"완료"}"""
    if BOOKMARK_FILE.exists():
        with open(BOOKMARK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_bookmark(benefit_name: str, status: str) -> None:
    """북마크 추가/수정."""
    DATA_DIR.mkdir(exist_ok=True)
    bm = load_bookmarks()
    bm[benefit_name] = status
    with open(BOOKMARK_FILE, "w", encoding="utf-8") as f:
        json.dump(bm, f, ensure_ascii=False, indent=2)


def remove_bookmark(benefit_name: str) -> None:
    """북마크 삭제."""
    bm = load_bookmarks()
    bm.pop(benefit_name, None)
    with open(BOOKMARK_FILE, "w", encoding="utf-8") as f:
        json.dump(bm, f, ensure_ascii=False, indent=2)
