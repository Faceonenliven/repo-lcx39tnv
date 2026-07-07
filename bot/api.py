"""Async client for the NFA Resell API (https://nfa-api.acode.ing)."""

import os

import aiohttp

BASE_URL = os.environ.get("NFA_API_BASE", "https://nfa-api.acode.ing/api/v1")

# status-coin-bot coin API (optional). When both COIN_API_BASE and
# COIN_API_KEY are set, the shop bot's Leaderboard button ranks users by coins
# from that bot instead of local redemption counts. Read lazily so values from
# .env (loaded after import) are picked up.


def coin_api_configured() -> bool:
    return bool(os.environ.get("COIN_API_BASE")) and bool(os.environ.get("COIN_API_KEY"))


class APIError(Exception):
    """Raised when the API returns status != success or an HTTP error occurs."""


def _api_key() -> str:
    return os.environ["NFA_API_KEY"]


async def _request(method: str, path: str, *, params=None, json=None) -> dict:
    headers = {"X-API-Key": _api_key()}
    url = f"{BASE_URL}{path}"
    timeout = aiohttp.ClientTimeout(total=90)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.request(method, url, params=params, json=json, headers=headers) as resp:
            try:
                data = await resp.json()
            except aiohttp.ContentTypeError:
                text = await resp.text()
                raise APIError(f"Unexpected response (HTTP {resp.status}): {text[:200]}")
    if not isinstance(data, dict):
        raise APIError("Unexpected response shape from API")
    if data.get("status") != "success":
        raise APIError(data.get("message") or "Request failed")
    return data


async def get_status() -> dict:
    return await _request("GET", "/status")


async def get_stock() -> dict[str, int]:
    data = await _request("GET", "/stock")
    return data.get("stock", {})


async def get_accounts() -> dict[str, float]:
    """Returns {account_type: price_usd}."""
    data = await _request("GET", "/accounts")
    return data.get("accounts", {})


async def activate(activation_key: str) -> dict:
    """Activate an existing key. Returns the full response (account, jwt_token, exe_base64...)."""
    return await _request("POST", "/activate", json={"activation_key": activation_key})


async def create_keys(account_type: str, amount: int) -> list[str]:
    data = await _request(
        "POST", "/create_keys", json={"account_type": account_type, "amount": amount}
    )
    return data.get("keys", [])


async def key_details(activation_key: str) -> dict:
    return await _request("GET", "/key_details", params={"activation_key": activation_key})


async def coin_leaderboard(limit: int = 10) -> list[tuple[int, int]]:
    """Fetch the top coin holders from status-coin-bot. Returns [(user_id, coins)]."""
    base = os.environ["COIN_API_BASE"].rstrip("/")
    url = f"{base}/api/coins/leaderboard"
    headers = {"X-API-Key": os.environ["COIN_API_KEY"]}
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, params={"limit": limit}, headers=headers) as resp:
            if resp.status != 200:
                raise APIError(f"Coin API returned HTTP {resp.status}")
            data = await resp.json()
    entries = data.get("leaderboard", []) if isinstance(data, dict) else []
    return [(int(e["user_id"]), int(e["coins"])) for e in entries]
