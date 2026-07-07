"""JSON-backed storage for products, license keys, and redemption stats."""

import json
import threading
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data.json"

_lock = threading.Lock()

_DEFAULT = {
    "products": {},
    "leaderboard": {},
}


def _load() -> dict:
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return json.loads(json.dumps(_DEFAULT))


def _save(data: dict) -> None:
    tmp = DATA_FILE.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    tmp.replace(DATA_FILE)


def add_product(name: str) -> bool:
    with _lock:
        data = _load()
        key = name.lower()
        if key in data["products"]:
            return False
        data["products"][key] = {"display_name": name, "keys": []}
        _save(data)
        return True


def remove_product(name: str) -> bool:
    with _lock:
        data = _load()
        if data["products"].pop(name.lower(), None) is None:
            return False
        _save(data)
        return True


def add_keys(product: str, keys: list[str]) -> int:
    """Add keys to a product's stock. Returns number of keys added, -1 if no such product."""
    with _lock:
        data = _load()
        prod = data["products"].get(product.lower())
        if prod is None:
            return -1
        existing = set(prod["keys"])
        new_keys = [k for k in keys if k and k not in existing]
        prod["keys"].extend(new_keys)
        _save(data)
        return len(new_keys)


def get_stock() -> dict[str, int]:
    """Return {display_name: key_count} for all products."""
    data = _load()
    return {p["display_name"]: len(p["keys"]) for p in data["products"].values()}


def redeem_key(key: str, user_id: int) -> str | None:
    """Redeem a key. Returns the product display name if valid, else None."""
    with _lock:
        data = _load()
        for prod in data["products"].values():
            if key in prod["keys"]:
                prod["keys"].remove(key)
                uid = str(user_id)
                data["leaderboard"][uid] = data["leaderboard"].get(uid, 0) + 1
                _save(data)
                return prod["display_name"]
        return None


def get_leaderboard(limit: int = 10) -> list[tuple[int, int]]:
    """Return [(user_id, redemption_count)] sorted descending."""
    data = _load()
    entries = sorted(data["leaderboard"].items(), key=lambda x: x[1], reverse=True)
    return [(int(uid), count) for uid, count in entries[:limit]]
