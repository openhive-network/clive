from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding

from clive.ui.shared.cart_based_screen import CartBasedScreen
from clive.ui.widgets.big_title import BigTitle

if TYPE_CHECKING:
    from textual.app import ComposeResult


class TransferToAccount(CartBasedScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Operations"),
    ]

    def create_left_panel(self) -> ComposeResult:
        yield BigTitle("Transfer to account")
