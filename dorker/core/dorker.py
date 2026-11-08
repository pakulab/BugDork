from __future__ import annotations

import asyncio
from collections.abc import Iterable

from dorker.core.client import CSEClient
from dorker.core.keypool import KeyPool
from dorker.logging import Logger
from dorker.models import DorkResult, RunConfig


class Dorker:
    def __init__(self, client: CSEClient, pool: KeyPool, cfg: RunConfig):
        self._client = client
        self._pool = pool
        self._cfg = cfg

    async def _search_one(self, dork: str) -> DorkResult:
        urls: set[str] = set()
        start = 1
        cap = max(1, min(self._cfg.max_results, 100))
        while len(urls) < cap and self._pool:
            key = await self._pool.acquire()
            if key is None:
                break
            page, exhausted = await self._client.search(key, dork, start)
            if exhausted:
                await self._pool.exhaust(key)
                if self._cfg.verbose:
                    Logger(
                        f"Key exhausted, {self._pool.remaining} remaining",
                        "verbose",
                    )
                continue
            if not page:
                break
            remaining = cap - len(urls)
            urls.update(page[:remaining])
            if len(page) < 10 or len(urls) >= cap:
                break
            start += 10
        return DorkResult(dork=dork, urls=sorted(urls))

    async def run(self, dorks: Iterable[str]) -> list[DorkResult]:
        dorks = list(dict.fromkeys(dorks))
        sem = asyncio.Semaphore(self._cfg.threads)
        results: list[DorkResult] = []

        async def worker(d: str) -> None:
            async with sem:
                try:
                    res = await self._search_one(d)
                    results.append(res)
                    if res.urls:
                        Logger(f"{len(res.urls)} result(s) for: {d}")
                    elif self._cfg.verbose:
                        Logger(f"No results for: {d}", "warn")
                except asyncio.CancelledError:
                    raise
                except Exception as e:  # noqa: BLE001
                    Logger(f"Worker error for '{d}': {e}", "error")

        await asyncio.gather(*(worker(d) for d in dorks), return_exceptions=True)
        return results
