from __future__ import annotations

import httpx

from dorker import __repo__
from dorker.logging import Logger


def _api_url() -> str:
    """https://github.com/pakulab/BugDork -> https://api.github.com/repos/pakulab/BugDork"""
    repo_path = __repo__.rstrip("/").split("github.com/", 1)[-1]
    return f"https://api.github.com/repos/{repo_path}/releases/latest"


async def check_latest(timeout: float = 10.0) -> str | None:
    url = _api_url()
    try:
        async with httpx.AsyncClient(timeout=timeout) as c:
            r = await c.get(url, headers={"Accept": "application/vnd.github+json"})
        if r.status_code == 200:
            return r.json().get("tag_name")
        Logger(f"Version check HTTP {r.status_code}", "verbose")
    except Exception as e:  # noqa: BLE001
        Logger(f"Version check failed: {e}", "verbose")
    return None
