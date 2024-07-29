from __future__ import annotations

from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from rich.text import TextType

SHORTCUT_STYLING: Final[str] = "yellow italic"
SYSTEM_COLOR: Final[str] = "cyan"
SOON_STYLING: Final[str] = "#FF8C00"
SOON_LABEL: Final[str] = f"[{SOON_STYLING}]soon[/]"


def colorize_shortcut(message: str) -> str:
    return f"[{SHORTCUT_STYLING}]{message}[/]"


def colorize_system_text(message: str) -> str:
    return f"[{SYSTEM_COLOR}]{message}[/]"


def label_future_functionality(message: TextType) -> str:
    return f"{message} {SOON_LABEL}"
