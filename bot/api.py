"""Async client for the NFA Resell API (https://nfa-api.acode.ing)."""

import os

import aiohttp

BASE_URL = os.environ.get("NFA_API_BASE", "https://nfa-api.acode.ing/api/v1")


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
