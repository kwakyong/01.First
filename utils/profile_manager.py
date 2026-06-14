import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
PROFILE_FILE = DATA_DIR / "user_profile.json"


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
