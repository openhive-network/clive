from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.cart_based_screen.cart_based_screen import CartBasedScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset, Operation
from schemas.operations import ClaimAccountOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title"""


class ClaimAccount(CartBasedScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f2", "add_to_cart", "Add to cart"),
        Binding("f5", "fast_broadcast", "Fast broadcast"),
        Binding("f10", "finalize", "Finalize transaction"),
    ]

    def __init__(self) -> None:
        super().__init__()

        self.__creator_input = Input(placeholder="e.g.: alice")
        self.__fee_input = Input(placeholder="e.g.: 1.000. Notice: if you want to pay in RC type 0")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Claim account")
            with Body():
                yield Static("creator", classes="label")
                yield self.__creator_input
                yield Static("fee", classes="label")
                yield self.__fee_input

    def _create_operation(self) -> Operation | None:
        return ClaimAccountOperation(creator=self.__creator_input.value, fee=Asset.hive(float(self.__fee_input.value)))
