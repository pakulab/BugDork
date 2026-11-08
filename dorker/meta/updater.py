import asyncio
import sys

from dorker import __repo__
from dorker.logging import Logger


async def self_update(yes: bool = False) -> int:
    if not yes:
        Logger("Refusing to self-update without --yes. Run manually:", "warn")
        Logger(f"  pip install -U git+{__repo__}", "warn")
        return 2

    cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "-U",
        f"git+{__repo__}",
    ]
    Logger("Updating BugDork...", "info")
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, err = await proc.communicate()
    if proc.returncode == 0:
        Logger("Update complete.", "info")
        return 0
    Logger(f"Update failed: {err.decode(errors='replace')}", "warn")
    return 1
