from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import ValidationError
from textual.binding import Binding
from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.cart_based_screen.cart_based_screen import CartBasedScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.currency_selector_liquid import CurrencySelectorLiquid
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.notification import Notification
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset, Operation
from schemas.operations import EscrowTransferOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title"""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid"""


class AdditionalPlaceTaker(Static):
    """Additional container for making correct layout for Inputs, except fee"""


class EscrowTransfer(CartBasedScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f2", "add_to_cart", "Add to cart"),
        Binding("f5", "fast_broadcast", "Fast broadcast"),
        Binding("f10", "finalize", "Finalize transaction"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.__to_input = Input(placeholder="e.g: alice")
        self.__agent_input = Input(placeholder="e.g: bob")
        self.__escrow_id_input = Input(placeholder="e.g.: 23456789. Notice - default is 30")
        self.__hbd_amount_input = Input(placeholder="Notice: if don't want to use, leave 0.000 here", value="0.000")
        self.__hive_amount_input = Input(placeholder="Notice: if don't want to use, leave 0.000 here", value="0.000")
        self.__fee_input = Input(placeholder="e.g: 3.000")
        self.__ratification_deadline_input = Input(placeholder="e.g: 2023-07-26T11:22:39")
        self.__escrow_expiration_input = Input(placeholder="e.g: 2023-07-26T11:22:39")
        self.__json_meta_input = Input(placeholder="e.g: {}")
        self.__currency_selector = CurrencySelectorLiquid()

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Escrow transfer")
            with Body():
                yield Static("from", classes="label")
                yield EllipsedStatic(str(self.app.world.profile_data.working_account.name), id_="from-label")
                yield AdditionalPlaceTaker()
                yield Static("to", classes="label")
                yield self.__to_input
                yield Static("agent", classes="label")
                yield self.__agent_input
                yield Static("escrow id", classes="label")
                yield self.__escrow_id_input
                yield Static("hbd amount", classes="label")
                yield self.__hbd_amount_input
                yield Static("hive amount", classes="label")
                yield self.__hive_amount_input
                yield Static("ratification deadline", classes="label")
                yield self.__ratification_deadline_input
                yield Static("escrow expiration", classes="label")
                yield self.__escrow_expiration_input
                yield Static("json meta", classes="label")
                yield self.__json_meta_input
                yield PlaceTaker()
                yield Static("fee", classes="label")
                yield self.__fee_input
                yield self.__currency_selector

    def create_operation(self) -> Operation | None:
        try:
            if self.__escrow_id_input.value:
                return EscrowTransferOperation(
                    from_=str(self.app.world.profile_data.name),
                    to=self.__to_input.value,
                    agent=self.__agent_input.value,
                    escrow_id=int(self.__escrow_id_input.value),
                    hbd_amount=Asset.hbd(float(self.__hbd_amount_input.value)),
                    hive_amount=Asset.hive(float(self.__hive_amount_input.value)),
                    ratification_deadline=self.__ratification_deadline_input.value,
                    escrow_expiration=self.__ratification_deadline_input.value,
                    json_meta=self.__json_meta_input.value,
                    fee=self.__currency_selector.selected.value(float(self.__fee_input.value)),
                )
            return EscrowTransferOperation(  # noqa: TRY300
                from_=str(self.app.world.profile_data.name),
                to=self.__to_input.value,
                agent=self.__agent_input.value,
                hbd_amount=Asset.hbd(float(self.__hbd_amount_input.value)),
                hive_amount=Asset.hive(float(self.__hive_amount_input.value)),
                ratification_deadline=self.__ratification_deadline_input.value,
                escrow_expiration=self.__ratification_deadline_input.value,
                json_meta=self.__json_meta_input.value,
                fee=self.__currency_selector.selected.value(float(self.__fee_input.value)),
            )
        except ValidationError as error:
            Notification(f"Operation failed the validation process.\n{error}", category="error").show()
            return None
