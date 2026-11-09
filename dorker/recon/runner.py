from __future__ import annotations

from pathlib import Path

from dorker.recon.common import clean_results, normalize_target
from dorker.recon.providers import run_gau, run_katana, run_wayback


def run_recon(
    target: str,
    *,
    output: str,
    fmt: str = "txt",
    active: bool = False,
    include_subdomains: bool = False,
    tool_mode: str = "auto",
    max_urls: int = 10000,
    user_agent: str = "BugDork/3.0",
    rate_limit: int = 2,
    concurrency: int = 2,
) -> list[str]:
    domain = normalize_target(target)
    collected: list[str] = []
    # Passive sources are always run first.
    collected.extend(run_gau(domain, mode=tool_mode))
    collected.extend(
        run_wayback(domain, user_agent=user_agent, limit=min(max_urls, 5000))
    )
    if active:
        collected.extend(
            run_katana(
                domain, mode=tool_mode, rate_limit=rate_limit, concurrency=concurrency
            )
        )
    urls = clean_results(collected, domain, include_subdomains, max_urls)
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "txt":
        destination.write_text("".join(url + "\n" for url in urls), encoding="utf-8")
    elif fmt == "json":
        import json

        destination.write_text(
            json.dumps({"target": domain, "count": len(urls), "urls": urls}, indent=2),
            encoding="utf-8",
        )
    elif fmt == "csv":
        import csv

        with destination.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["url"])
            writer.writerows([[url] for url in urls])
    else:
        raise ValueError("Output format must be txt, json, or csv.")
    return urls
