from __future__ import annotations

from clive.__private.ui.widgets.buttons.one_line_button import OneLineButton
from clive.__private.ui.widgets.buttons.clive_button import CliveButton


class FinalizeTransactionButton(CliveButton):
    class Pressed(CliveButton.Pressed):
        """Used to identify exactly that FinalizeTransaction button was pressed."""

        DEFAULT_CSS = """
            AddToCartButton {
                width: 25;
            }
            """

    def __init__(self) -> None:
        super().__init__("Finalize transaction (F6)", variant="success", id_="finalize-button")


class FinalizeTransactionOneLineButton(OneLineButton, FinalizeTransactionButton):
    class Pressed(FinalizeTransactionButton.Pressed):
        """Message sent when FinalizeTransactionOneLineButton is pressed."""
