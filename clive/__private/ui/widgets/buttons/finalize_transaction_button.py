from __future__ import annotations

from clive.__private.core.constants.tui.bindings import FINALIZE_TRANSACTION_BINDING_KEY
from clive.__private.ui.widgets.buttons.clive_button import CliveButton
from clive.__private.ui.widgets.buttons.one_line_button import OneLineButton


class FinalizeTransactionButton(CliveButton):
    DEFAULT_CSS = """
    FinalizeTransactionButton {
        width: 29;
    }
    """

    class Pressed(CliveButton.Pressed):
        """Used to identify exactly that FinalizeTransactionButton was pressed."""

    def __init__(self) -> None:
        super().__init__(
            f"Finalize transaction ({FINALIZE_TRANSACTION_BINDING_KEY})", variant="success", id_="finalize-button"
        )


class FinalizeTransactionOneLineButton(OneLineButton, FinalizeTransactionButton):
    class Pressed(FinalizeTransactionButton.Pressed):
        """Message sent when FinalizeTransactionOneLineButton is pressed."""
