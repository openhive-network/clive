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
            "Finalize transaction",
            variant="success",
            binding=self.custom_bindings.operations.finalize_transaction,
            id_="finalize-button",
        )
