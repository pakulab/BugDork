import asyncio
import json
import random

import httpx

from dorker.logging import Logger
from dorker.models import Key

CSE_URL = "https://customsearch.googleapis.com/customsearch/v1"
_QUOTA_REASONS = {"quotaExceeded", "rateLimitExceeded", "dailyLimitExceeded"}


def _is_quota(status: int, body: str) -> bool:
    if status in (403, 429):
        return True
    try:
        err = json.loads(body).get("error") or {}
        return any(e.get("reason") in _QUOTA_REASONS for e in err.get("errors", []))
    except Exception:  # noqa: BLE001
        return False


class CSEClient:
    def __init__(
        self,
        client: httpx.AsyncClient,
        timeout: float,
        retries: int,
        delay: float,
        verbose: bool = False,
    ):
        self._c = client
        self._timeout = timeout
        self._retries = retries
        self._delay = delay
        self._verbose = verbose

    async def search(self, key: Key, dork: str, start: int) -> tuple[list[str], bool]:
        """Return (urls, key_exhausted)."""
        params = {
            "q": dork,
            "cx": key.cx_id,
            "num": 10,
            "start": start,
            "key": key.api_key,
            "alt": "json",
        }
        for attempt in range(1, self._retries + 1):
            try:
                await asyncio.sleep(self._delay)
                r = await self._c.get(CSE_URL, params=params, timeout=self._timeout)
                if r.status_code == 200:
                    items = r.json().get("items") or []
                    return [it["link"] for it in items if it.get("link")], False
                if _is_quota(r.status_code, r.text):
                    return [], True
                if r.status_code in (500, 502, 503, 504) and attempt < self._retries:
                    backoff = min(2**attempt, 30) + random.uniform(0, 1)
                    if self._verbose:
                        Logger(
                            f"HTTP {r.status_code}, retry {attempt}/{self._retries} "
                            f"in {backoff:.1f}s",
                            "verbose",
                        )
                    await asyncio.sleep(backoff)
                    continue
                Logger(f"CSE HTTP {r.status_code} for '{dork}'", "error")
                return [], False
            except (httpx.ReadTimeout, httpx.ConnectTimeout):
                if attempt < self._retries:
                    await asyncio.sleep(min(2**attempt, 15))
                    continue
                Logger(f"Timeout for '{dork}' after {self._retries} retries", "error")
                return [], False
            except httpx.HTTPError as e:
                Logger(f"HTTP error for '{dork}': {e}", "error")
                return [], False
        return [], False
