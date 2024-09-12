from __future__ import annotations

from clive.__private.ui.widgets.buttons.one_line_button import OneLineButton


class PageUpButton(OneLineButton):
    class Pressed(OneLineButton.Pressed):
        """Message send when PageUpButton is pressed."""

    def __init__(self) -> None:
        super().__init__("↑ PgUp", variant="transparent", id_="page-up-button")


class PageDownButton(OneLineButton):
    class Pressed(OneLineButton.Pressed):
        """Message send when PageDownButton is pressed."""

    def __init__(self) -> None:
        super().__init__("↓ PgDn", variant="transparent", id_="page-down-button")
