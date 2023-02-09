from __future__ import annotations

from typing import TYPE_CHECKING

from clive.get_clive import get_clive

if TYPE_CHECKING:
    from prompt_toolkit.layout.layout import FocusableElement


def set_focus(container: FocusableElement) -> None:
    get_clive().set_focus(container)
