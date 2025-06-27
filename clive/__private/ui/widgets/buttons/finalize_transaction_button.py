from __future__ import annotations

from clive.__private.ui.widgets.buttons.one_line_button import OneLineButton


class FinalizeTransactionButton(OneLineButton):
    DEFAULT_CSS = """
    FinalizeTransactionButton {
        width: 29;
    }
    """

    class Pressed(OneLineButton.Pressed):
        """Used to identify exactly that FinalizeTransactionButton was pressed."""

    def __init__(self) -> None:
        super().__init__(
            f"Finalize transaction ({self.app.custom_bindings.operations.finalize_transaction})",
            variant="success",
            id_="finalize-button",
        )
