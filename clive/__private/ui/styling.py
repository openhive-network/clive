from __future__ import annotations

from typing import Final

SHORTCUT_STYLING: Final[str] = "yellow italic"
SYSTEM_COLOR: Final[str] = "cyan"


def colorize_shortcut(message: str) -> str:
    return f"[{SHORTCUT_STYLING}]{message}[/]"


def colorize_system_text(message: str) -> str:
    return f"[{SYSTEM_COLOR}]{message}[/]"
