from __future__ import annotations

import os

import aiofiles

from dorker.models import DorkResult
from dorker.output.formatters import FORMATTERS


class OutputWriter:
    def __init__(self, path: str, fmt: str = "txt"):
        if fmt not in FORMATTERS:
            raise ValueError(f"Unsupported format: {fmt}")
        self._path = path
        self._fmt = fmt
        # Sync-safe: prepare parent dir once, not inside async write()
        parent = os.path.dirname(os.path.abspath(path))
        if parent:
            os.makedirs(parent, exist_ok=True)

    async def write(self, results: list[DorkResult], append: bool = False) -> None:
        mode = "a" if append and self._fmt == "txt" else "w"
        data = FORMATTERS[self._fmt](results)
        async with aiofiles.open(self._path, mode, encoding="utf-8") as f:
            await f.write(data)
