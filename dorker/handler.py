from __future__ import annotations

import asyncio
import os
import random
import sys

import httpx

from dorker import __version__
from dorker.cli import build_parser, parse_args
from dorker.config import ensure_config, load_keys
from dorker.core.client import CSEClient
from dorker.core.dorker import Dorker
from dorker.core.keypool import KeyPool
from dorker.exceptions import InputError, NoKeysError
from dorker.logging import Logger, stderr
from dorker.meta.updater import self_update
from dorker.meta.version import check_latest
from dorker.models import RunConfig
from dorker.output import OutputWriter
from dorker.recon.common import normalize_target
from dorker.recon.filter import filter_file
from dorker.recon.runner import run_recon
from dorker.ui.banner import banner


def _read_lines(path: str) -> list[str]:
    """Blocking read — run via asyncio.to_thread."""
    with open(path, encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip()]


def _read_list(path: str) -> list[str]:
    if not os.path.isfile(path):
        raise InputError(f"List file not found: {path}")
    with open(path, encoding="utf-8") as f:
        out = [ln.strip() for ln in f if ln.strip() and not ln.strip().startswith("#")]
    if not out:
        raise InputError(f"No dorks in {path}")
    return out


async def _read_stdin() -> list[str]:
    if sys.stdin.isatty():
        raise InputError("No input provided. Use -q, -l, or pipe dorks via stdin.")
    lines = [ln.strip() for ln in sys.stdin if ln.strip()]
    if not lines:
        raise InputError("Empty stdin input.")
    return lines


async def _print_version(cfg: RunConfig) -> None:
    if cfg.silent:
        return
    latest = await check_latest()
    if latest is None:
        Logger("Unable to determine latest version.", "verbose")
        return
    status = "latest" if latest == __version__ else "outdated"
    Logger(f"bugdork {__version__} ({status}, latest={latest})", "info")


async def _resolve_proxy(cfg: RunConfig) -> str | None:
    proxy = cfg.proxy
    if cfg.proxy_file:
        try:
            pool = await asyncio.to_thread(_read_lines, cfg.proxy_file)
            if pool:
                proxy = random.choice(pool)
        except OSError as e:
            Logger(f"proxy-file error: {e}", "warn")
    return proxy


async def run() -> int:
    cfg = parse_args()

    if cfg.help:
        stderr(banner())
        build_parser().print_help()
        return 0

    if not cfg.silent:
        stderr(banner())
        await _print_version(cfg)

    if cfg.update:
        latest = await check_latest()
        if latest and latest == __version__:
            Logger("Already on latest version.", "info")
            return 0
        return await self_update(yes=False)

    # Recon and URL filtering are independent of Google CSE credentials.
    if cfg.urls_only or cfg.recon:
        if not cfg.target:
            raise InputError("Recon requires -T/--target example.com.")
        target = normalize_target(cfg.target)
        active = bool(cfg.active)
        if active:
            Logger(
                "ACTIVE Katana crawl sends requests to the live target. "
                "Use only with explicit authorization.",
                "warn",
            )
            # Gunakan asyncio.to_thread untuk elak block async event loop
            confirmation = (
                (
                    await asyncio.to_thread(
                        input, f"Type '{target}' to confirm active crawl: "
                    )
                )
                .strip()
                .lower()
            )
            if confirmation != target:
                Logger("Confirmation mismatch; active crawl cancelled.", "warn")
                return 2
        output = cfg.output or os.path.join(
            "output", f"{target.replace('.', '_')}_urls.{cfg.fmt}"
        )
        urls = await asyncio.to_thread(
            run_recon,
            target,
            output=output,
            fmt=cfg.fmt,
            active=active,
            include_subdomains=cfg.include_subdomains,
            tool_mode=cfg.tool_mode,
            max_urls=cfg.max_urls,
        )
        Logger(f"Recon complete: {len(urls)} in-scope URL(s) saved to {output}", "info")
        return 0 if urls else 1

    if cfg.filter_pattern:
        if not cfg.list_file:
            raise InputError("--filter requires -l/--list URL file.")
        matches = await asyncio.to_thread(
            filter_file, cfg.list_file, cfg.filter_pattern
        )
        if cfg.output:
            writer = OutputWriter(cfg.output, cfg.fmt)
            from dorker.models import DorkResult

            await writer.write([DorkResult(dork=cfg.filter_pattern, urls=matches)])
            Logger(f"Saved {len(matches)} matching URL(s) to {cfg.output}", "info")
        else:
            for url in matches:
                print(url)
            Logger(f"Matched {len(matches)} URL(s)", "info")
        return 0 if matches else 1

    # Input
    if cfg.query:
        dorks = [cfg.query]
    elif cfg.list_file:
        dorks = await asyncio.to_thread(_read_list, cfg.list_file)
    else:
        dorks = await _read_stdin()

    # Config + keys
    path = ensure_config(cfg.config_path)
    keys = await load_keys(path)
    if not keys:
        raise NoKeysError("No API keys configured.")

    # Proxy
    proxy = await _resolve_proxy(cfg)

    limits = httpx.Limits(
        max_connections=cfg.threads * 2,
        max_keepalive_connections=cfg.threads,
    )

    async with httpx.AsyncClient(
        proxy=proxy,
        verify=True,
        timeout=httpx.Timeout(cfg.timeout),
        limits=limits,
        max_redirects=30,
    ) as http:
        client = CSEClient(http, cfg.timeout, cfg.max_retries, cfg.delay, cfg.verbose)
        pool = KeyPool(keys)
        dorker = Dorker(client, pool, cfg)
        results = await dorker.run(dorks)

    # Output
    if cfg.output:
        writer = OutputWriter(cfg.output, cfg.fmt)
        await writer.write(results)
        total = sum(len(r.urls) for r in results)
        Logger(f"Saved {total} URL(s) to {cfg.output}", "info")
    else:
        for r in results:
            for u in r.urls:
                print(u)

    return 0 if any(r.urls for r in results) else 1
