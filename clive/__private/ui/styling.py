from __future__ import annotations

from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from rich.text import TextType

SHORTCUT_STYLING: Final[str] = "$accent italic"
SYSTEM_STYLING: Final[str] = "$success"
SOON_STYLING: Final[str] = "$accent italic"
SOON_TEXT: Final[str] = "soon"


def colorize_shortcut(shortcut: str) -> str:
    return f"[{SHORTCUT_STYLING}]{shortcut}[/]"


def colorize_system_text(system: str) -> str:
    return f"[{SYSTEM_STYLING}]{system}[/]"


def label_future_functionality(message: TextType) -> str:
    return f"{message} [{SOON_STYLING}]{SOON_TEXT}[/]"
