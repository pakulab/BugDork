from __future__ import annotations

import re
from pathlib import Path


def filter_urls(urls: list[str], pattern: str) -> list[str]:
    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error as exc:
        raise ValueError(f"Invalid filter regex: {exc}") from exc
    return [url for url in urls if regex.search(url)]


def filter_file(path: str, pattern: str) -> list[str]:
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"URL list not found: {path}")
    return filter_urls(
        file_path.read_text(encoding="utf-8", errors="replace").splitlines(), pattern
    )
