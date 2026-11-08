import re
import sys

from colorama import Fore, Style, init

init(autoreset=True)

_BOLD = Style.BRIGHT
_RESET = Style.RESET_ALL
_COLORS = {
    "info": Fore.BLUE,
    "warn": Fore.RED,
    "error": Fore.YELLOW,
    "verbose": Fore.GREEN,
}


def redact(text: str) -> str:
    text = re.sub(r"(key=)[^&\s]+", r"\1***", text)
    text = re.sub(r"(cx=)[^&\s]+", r"\1***", text)
    return text


def Logger(message: str, level: str = "info") -> None:
    color = _COLORS.get(level, Fore.MAGENTA)
    label = level.upper()[:4]
    print(
        f"{_BOLD}{Fore.WHITE}[{_RESET}{_BOLD}{color}{label}{_RESET}"
        f"{_BOLD}{Fore.WHITE}]{_RESET}: {_BOLD}{Fore.WHITE}{redact(str(message))}{_RESET}",
        file=sys.stderr,
    )


def stdout(message: str) -> None:
    print(message, file=sys.stdout)


def stderr(message: str) -> None:
    print(message, file=sys.stderr)
