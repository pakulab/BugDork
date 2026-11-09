from __future__ import annotations

import shutil
import subprocess

import httpx

WAYBACK_CDX = "https://web.archive.org/cdx/search/cdx"


def run_gau(target: str, mode: str = "auto", timeout: int = 180) -> list[str]:
    if mode in ("auto", "local") and shutil.which("gau"):
        command, input_data = ["gau", target], None
    elif mode in ("auto", "docker") and shutil.which("docker"):
        command, input_data = [
            "docker",
            "run",
            "--rm",
            "-i",
            "ghcr.io/lc/gau:latest",
        ], target + "\n"
    else:
        return []
    try:
        result = subprocess.run(
            command,
            input=input_data,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return result.stdout.splitlines() if result.returncode == 0 else []
    except (OSError, subprocess.TimeoutExpired):
        return []


def run_wayback(
    target: str, user_agent: str, timeout: float = 30, limit: int = 5000
) -> list[str]:
    params = {
        "url": target + "/*",
        "output": "text",
        "fl": "original",
        "collapse": "urlkey",
        "filter": "statuscode:200",
        "pageSize": min(limit, 5000),
    }
    try:
        response = httpx.get(
            WAYBACK_CDX,
            params=params,
            headers={"User-Agent": user_agent},
            timeout=timeout,
            follow_redirects=True,
        )
        response.raise_for_status()
        return response.text.splitlines()
    except httpx.HTTPError:
        return []


def run_katana(
    target: str,
    mode: str = "auto",
    rate_limit: int = 2,
    concurrency: int = 2,
    timeout: int = 300,
) -> list[str]:
    if not 1 <= rate_limit <= 10 or not 1 <= concurrency <= 5:
        raise ValueError("Katana limits: rate 1-10 req/s and concurrency 1-5.")
    args = [
        "-u",
        "https://" + target,
        "-silent",
        "-rl",
        str(rate_limit),
        "-c",
        str(concurrency),
        "-timeout",
        "10",
        "-retry",
        "1",
    ]
    if mode in ("auto", "local") and shutil.which("katana"):
        command = ["katana", *args]
    elif mode in ("auto", "docker") and shutil.which("docker"):
        command = ["docker", "run", "--rm", "projectdiscovery/katana:latest", *args]
    else:
        return []
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=timeout, check=False
        )
        return result.stdout.splitlines() if result.returncode == 0 else []
    except (OSError, subprocess.TimeoutExpired):
        return []
