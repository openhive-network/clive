from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from prompt_toolkit.layout.layout import FocusableElement


def set_focus(container: FocusableElement) -> None:
    from clive.app import clive

    clive.set_focus(container)
