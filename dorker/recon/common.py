from __future__ import annotations

import re
from urllib.parse import urlparse, urlunparse


def normalize_target(target: str) -> str:
    parsed = urlparse(target.strip() if "://" in target else "//" + target.strip())
    host = (parsed.hostname or "").lower().rstrip(".")
    if not host or not re.fullmatch(r"[a-z0-9.-]+", host) or ".." in host:
        raise ValueError("Invalid target. Supply a domain such as example.com.")
    return host


def normalize_url(value: str) -> str | None:
    try:
        p = urlparse(value.strip())
        if p.scheme not in ("http", "https") or not p.hostname:
            return None
        host = p.hostname.lower().rstrip(".")
        netloc = host + (f":{p.port}" if p.port else "")
        return urlunparse((p.scheme.lower(), netloc, p.path or "/", "", p.query, ""))
    except (ValueError, TypeError):
        return None


def in_scope(url: str, target: str, include_subdomains: bool = False) -> bool:
    host = (urlparse(url).hostname or "").lower().rstrip(".")
    return host == target or (include_subdomains and host.endswith("." + target))


def clean_results(
    urls, target: str, include_subdomains: bool = False, max_urls: int = 10000
):
    found = set()
    for item in urls:
        normalized = normalize_url(item)
        if normalized and in_scope(normalized, target, include_subdomains):
            found.add(normalized)
        if len(found) >= max_urls:
            break
    return sorted(found)
