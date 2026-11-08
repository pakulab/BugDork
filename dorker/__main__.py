import asyncio
import sys

from dorker.exceptions import DorkerError
from dorker.handler import run
from dorker.logging import Logger


def main() -> None:
    try:
        rc = asyncio.run(run())
    except KeyboardInterrupt:
        Logger("Interrupted by user.", "warn")
        rc = 130
    except DorkerError as e:
        Logger(str(e), "error")
        rc = e.exit_code
    except Exception as e:  # noqa: BLE001
        Logger(f"Unexpected error: {e} ({type(e).__name__})", "error")
        rc = 1
    sys.exit(rc)


if __name__ == "__main__":
    main()
