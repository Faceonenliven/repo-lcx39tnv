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


async def check_account(activation_key: str) -> dict:
    """Warranty check/replace for a key. Returns the raw response (result, replacement_key...)."""
    headers = {"X-API-Key": _api_key()}
    url = f"{BASE_URL}/check_account"
    timeout = aiohttp.ClientTimeout(total=60)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json={"activation_key": activation_key}, headers=headers) as resp:
                data = await resp.json(content_type=None)
    except (aiohttp.ClientError, ValueError) as e:
        raise APIError(f"Could not reach the replacement service: {e}")
    if not isinstance(data, dict):
        raise APIError("Unexpected response shape from API")
    return data


def _coin_base() -> str:
    base = os.environ["COIN_API_BASE"].strip().rstrip("/")
    if not base.startswith(("http://", "https://")):
        base = "https://" + base
    return base


async def _coin_request(method: str, path: str, *, params=None, json=None) -> dict:
    url = f"{_coin_base()}{path}"
    headers = {"X-API-Key": os.environ["COIN_API_KEY"]}
    timeout = aiohttp.ClientTimeout(total=30)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.request(method, url, params=params, json=json, headers=headers) as resp:
                data = await resp.json(content_type=None)
                if resp.status != 200:
                    msg = data.get("error") if isinstance(data, dict) else None
                    raise APIError(msg or f"Coin API returned HTTP {resp.status}")
    except (aiohttp.ClientError, ValueError) as e:
        raise APIError(f"Could not reach coin API: {e}")
    if not isinstance(data, dict):
        raise APIError("Unexpected response shape from coin API")
    return data


async def coin_leaderboard(limit: int = 10) -> list[tuple[int, int]]:
    """Fetch the top coin holders from status-coin-bot. Returns [(user_id, coins)]."""
    data = await _coin_request("GET", "/api/coins/leaderboard", params={"limit": limit})
    return [(int(e["user_id"]), int(e["coins"])) for e in data.get("leaderboard", [])]


async def coin_profile(user_id: int) -> dict:
    return await _coin_request("GET", "/api/coins/profile", params={"user_id": user_id})


async def coin_check(user_id: int) -> dict:
    return await _coin_request("GET", "/api/coins/check", params={"user_id": user_id})


async def coin_settings() -> dict:
    return await _coin_request("GET", "/api/coins/settings")


async def coin_store() -> dict:
    return await _coin_request("GET", "/api/coins/store")


async def coin_update_setting(key: str, value) -> dict:
    return await _coin_request("POST", "/api/coins/settings", json={"key": key, "value": value})


async def coin_pay(from_id: int, to_id: int, amount: int) -> dict:
    return await _coin_request(
        "POST", "/api/coins/pay", json={"from_id": from_id, "to_id": to_id, "amount": amount}
    )


async def coin_adjust(user_id: int, delta: int) -> dict:
    return await _coin_request("POST", "/api/coins/adjust", json={"user_id": user_id, "delta": delta})


async def coin_set(user_id: int, amount: int) -> dict:
    return await _coin_request("POST", "/api/coins/set", json={"user_id": user_id, "amount": amount})
