from __future__ import annotations

import csv
import io
import json

from dorker.models import DorkResult


def format_txt(results: list[DorkResult]) -> str:
    lines = [u for r in results for u in r.urls]
    return "\n".join(lines) + ("\n" if lines else "")


def format_json(results: list[DorkResult]) -> str:
    return (
        json.dumps(
            [{"dork": r.dork, "urls": r.urls} for r in results],
            indent=2,
        )
        + "\n"
    )


def format_csv(results: list[DorkResult]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["dork", "url"])
    for r in results:
        for u in r.urls:
            w.writerow([r.dork, u])
    return buf.getvalue()


FORMATTERS = {"txt": format_txt, "json": format_json, "csv": format_csv}
