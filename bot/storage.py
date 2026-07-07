"""JSON-backed storage for the local redemption leaderboard."""

import json
import threading
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data.json"

_lock = threading.Lock()


def _load() -> dict:
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"leaderboard": {}}


def _save(data: dict) -> None:
    tmp = DATA_FILE.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    tmp.replace(DATA_FILE)


def record_redemption(user_id: int) -> int:
    """Increment a user's redemption count. Returns the new total."""
    with _lock:
        data = _load()
        uid = str(user_id)
        data["leaderboard"][uid] = data["leaderboard"].get(uid, 0) + 1
        _save(data)
        return data["leaderboard"][uid]


def get_leaderboard(limit: int = 10) -> list[tuple[int, int]]:
    """Return [(user_id, redemption_count)] sorted descending."""
    data = _load()
    entries = sorted(data["leaderboard"].items(), key=lambda x: x[1], reverse=True)
    return [(int(uid), count) for uid, count in entries[:limit]]
