from __future__ import annotations

from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from pathlib import Path

    from rich.text import TextType

HIGHLIGHT_STYLING: Final[str] = "$accent italic"
SHORTCUT_STYLING: Final[str] = HIGHLIGHT_STYLING
SYSTEM_STYLING: Final[str] = "$success"
WITNESS_NAME_STYLING: Final[str] = HIGHLIGHT_STYLING
PATH_STYLING: Final[str] = HIGHLIGHT_STYLING
SOON_STYLING: Final[str] = HIGHLIGHT_STYLING
SOON_TEXT: Final[str] = "soon"


def colorize_shortcut(shortcut: str) -> str:
    return f"[{SHORTCUT_STYLING}]{shortcut}[/]"


def colorize_system_text(system: str) -> str:
    return f"[{SYSTEM_STYLING}]{system}[/]"


def colorize_witness_name(witness_name: str) -> str:
    return f"[{WITNESS_NAME_STYLING}]{witness_name}[/]"


def colorize_path(path: str | Path) -> str:
    return f"[{PATH_STYLING}]{path}[/]"


def label_future_functionality(message: TextType) -> str:
    return f"{message} [{SOON_STYLING}]{SOON_TEXT}[/]"
