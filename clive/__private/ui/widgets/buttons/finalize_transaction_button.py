from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.constants.tui.bindings import FINALIZE_TRANSACTION_BINDING_KEY
from clive.__private.ui.widgets.buttons import BindingButton
from clive.__private.ui.widgets.buttons.clive_button import CliveButton
from clive.__private.ui.widgets.buttons.one_line_button import OneLineButton

if TYPE_CHECKING:
    from textual.binding import Binding


class FinalizeTransactionButton(BindingButton):
    DEFAULT_CSS = """
    FinalizeTransactionButton {
        width: 29;
    }
    """

    class Pressed(CliveButton.Pressed):
        """Used to identify exactly that FinalizeTransactionButton was pressed."""

    def __init__(self, bindings_list: list[Binding]) -> None:
        super().__init__(FINALIZE_TRANSACTION_BINDING_KEY, bindings_list)


class FinalizeTransactionOneLineButton(OneLineButton, FinalizeTransactionButton):
    class Pressed(FinalizeTransactionButton.Pressed):
        """Message sent when FinalizeTransactionOneLineButton is pressed."""
