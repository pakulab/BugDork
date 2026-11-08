from __future__ import annotations

import os
import stat

import aiofiles
import appdirs
import yaml

from dorker.exceptions import ConfigError
from dorker.logging import Logger
from dorker.models import Key

TEMPLATE = """# BugDork provider config
# Format: - API_KEY:CX_ID  (one per line under google:)
google:
#  - YOUR_API_KEY:YOUR_CSE_ID
"""


def default_path() -> str:
    return os.path.join(appdirs.user_config_dir(), "bugdork", "provider-config.yaml")


def _secure(path: str) -> None:
    try:
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass


def ensure_config(custom: str | None = None) -> str:
    path = custom or default_path()
    if custom and not os.path.isfile(path):
        raise ConfigError(f"Custom config not found: {path}")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(TEMPLATE)
        _secure(path)
        Logger(f"Created config template at {path}. Add your API keys.", "warn")
    _secure(path)
    return path


def _parse_entry(entry) -> Key | None:
    if isinstance(entry, str):
        parts = entry.split(":", 1)
        if len(parts) == 2 and parts[0].strip() and parts[1].strip():
            return Key(parts[0].strip(), parts[1].strip())
    elif isinstance(entry, dict):
        for k, v in entry.items():
            if k and v:
                return Key(str(k).strip(), str(v).strip())
    return None


async def load_keys(path: str, source: str = "google") -> list[Key]:
    try:
        async with aiofiles.open(path, encoding="utf-8") as f:
            data = yaml.safe_load(await f.read()) or {}
    except FileNotFoundError:
        raise ConfigError(f"Config not found: {path}") from None
    except PermissionError:
        raise ConfigError(f"Permission denied: {path}") from None
    except yaml.YAMLError as e:
        raise ConfigError(f"Invalid YAML in {path}: {e}") from e

    entries = data.get(source) or []
    keys = [k for k in (_parse_entry(e) for e in entries) if k]
    if not keys:
        raise ConfigError(
            f"No valid keys in {path}. Expected 'google: [- API_KEY:CX_ID]'."
        )
    return keys
