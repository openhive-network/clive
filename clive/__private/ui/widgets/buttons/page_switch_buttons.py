from __future__ import annotations

from clive.__private.ui.widgets.buttons import CliveButton
from clive.__private.ui.widgets.buttons.one_line_button import OneLineButton


class PageUpButton(CliveButton):
    class Pressed(CliveButton.Pressed):
        """Message sent when PageUpButton is pressed."""

    def __init__(self) -> None:
        super().__init__("↑ PgUp", variant="transparent", id_="page-up-button")


class PageUpOneLineButton(OneLineButton, PageUpButton):
    class Pressed(PageUpButton.Pressed):
        """Message sent when PageUpOneLineButton is pressed."""


class PageDownButton(CliveButton):
    class Pressed(CliveButton.Pressed):
        """Message sent when PageDownButton is pressed."""

    def __init__(self) -> None:
        super().__init__("↓ PgDn", variant="transparent", id_="page-down-button")


class PageDownOneLineButton(OneLineButton, PageDownButton):
    class Pressed(PageDownButton.Pressed):
        """Message sent when PageDownOneLineButton is pressed."""
