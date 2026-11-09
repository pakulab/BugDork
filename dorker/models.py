from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Key:
    api_key: str
    cx_id: str

    def __repr__(self) -> str:
        return f"Key(api_key='***', cx_id='{self.cx_id}')"


@dataclass
class DorkResult:
    dork: str
    urls: list[str] = field(default_factory=list)


@dataclass
class RunConfig:
    query: str | None = None
    list_file: str | None = None
    output: str | None = None
    fmt: str = "txt"
    threads: int = 20
    delay: float = 1.0
    timeout: float = 15.0
    max_results: int = 100
    max_retries: int = 3
    proxy: str | None = None
    proxy_file: str | None = None
    config_path: str | None = None
    update: bool = False
    verbose: bool = False
    silent: bool = False
    help: bool = False
    target: str | None = None
    recon: bool = False
    urls_only: bool = False
    filter_pattern: str | None = None
    active: bool = False
    tool_mode: str = "auto"
    include_subdomains: bool = False
    max_urls: int = 10000
