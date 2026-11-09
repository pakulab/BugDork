from __future__ import annotations

import argparse
import sys

from dorker.logging import Logger
from dorker.models import RunConfig


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="bugdork",
        add_help=False,
        usage=argparse.SUPPRESS,
        description="BugDork - Google dorking for ethical hackers",
    )
    p.add_argument("-q", "--query", type=str)
    p.add_argument(
        "-T",
        "--target",
        type=str,
        help="Target domain for authorized URL reconnaissance",
    )
    p.add_argument(
        "--recon",
        action="store_true",
        help="Run passive URL discovery; add --active for live Katana crawl",
    )
    p.add_argument(
        "--urls-only",
        action="store_true",
        help="Collect URLs from passive sources only",
    )
    p.add_argument(
        "--filter",
        dest="filter_pattern",
        type=str,
        help="Regex to filter an existing URL list (-l)",
    )
    p.add_argument(
        "--active",
        action="store_true",
        help="Enable live Katana crawl (requires typed confirmation)",
    )
    p.add_argument("--tool-mode", choices=["auto", "docker", "local"], default="auto")
    p.add_argument("--include-subdomains", action="store_true")
    p.add_argument("--max-urls", type=int, default=10000)
    p.add_argument("-l", "--list", dest="list_file", type=str)
    p.add_argument("-o", "--output", type=str)
    p.add_argument(
        "--format", dest="fmt", choices=["txt", "json", "csv"], default="txt"
    )
    p.add_argument("-t", "--threads", type=int, default=20)
    p.add_argument("-d", "--delay", type=float, default=1.0)
    p.add_argument("-to", "--timeout", type=float, default=15.0)
    p.add_argument("--max-results", type=int, default=100)
    p.add_argument("--max-retries", type=int, default=3)
    p.add_argument("-px", "--proxy", type=str)
    p.add_argument("--proxy-file", type=str)
    p.add_argument("-cp", "--config-path", type=str)
    p.add_argument("-up", "--update", action="store_true")
    p.add_argument("-v", "--verbose", action="store_true")
    p.add_argument("-s", "--silent", action="store_true")
    p.add_argument("-h", "--help", action="store_true")
    return p


def parse_args(argv: list[str] | None = None) -> RunConfig:
    parser = build_parser()
    try:
        ns = parser.parse_args(argv)
    except SystemExit:
        Logger("Invalid arguments. Run 'bugdork -h' for usage.", "warn")
        sys.exit(2)

    if ns.max_urls < 1:
        Logger("--max-urls must be >= 1", "warn")
        sys.exit(2)
    if ns.active and not (ns.recon and ns.target):
        Logger("--active requires --recon and --target", "warn")
        sys.exit(2)
    if ns.threads < 1:
        Logger("--threads must be >= 1", "warn")
        sys.exit(2)
    if ns.max_results < 1 or ns.max_results > 100:
        Logger("--max-results must be between 1 and 100", "warn")
        sys.exit(2)
    if ns.max_retries < 1:
        Logger("--max-retries must be >= 1", "warn")
        sys.exit(2)

    return RunConfig(
        query=ns.query,
        list_file=ns.list_file,
        output=ns.output,
        fmt=ns.fmt,
        threads=ns.threads,
        delay=ns.delay,
        timeout=ns.timeout,
        max_results=ns.max_results,
        max_retries=ns.max_retries,
        proxy=ns.proxy,
        proxy_file=ns.proxy_file,
        config_path=ns.config_path,
        update=ns.update,
        verbose=ns.verbose,
        silent=ns.silent,
        help=ns.help,
        target=ns.target,
        recon=ns.recon,
        urls_only=ns.urls_only,
        filter_pattern=ns.filter_pattern,
        active=ns.active,
        tool_mode=ns.tool_mode,
        include_subdomains=ns.include_subdomains,
        max_urls=ns.max_urls,
    )
