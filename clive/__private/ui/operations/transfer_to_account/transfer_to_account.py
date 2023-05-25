from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from pydantic import ValidationError
from textual.binding import Binding
from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.activate.activate import Activate
from clive.__private.ui.operations.cart import Cart
from clive.__private.ui.operations.cart_based_screen.cart_based_screen import CartBasedScreen
from clive.__private.ui.operations.tranaction_summary import TransactionSummary
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.notification import Notification
from clive.__private.ui.widgets.select.select import Select
from clive.__private.ui.widgets.select.select_item import SelectItem
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models.asset import Asset, AssetT
from clive.models.transfer_operation import TransferOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title"""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class CurrencySelector(Select[Callable[[float], AssetT]]):
    def __init__(self) -> None:
        def _asset_factory(symbol: str) -> Callable[[float], AssetT]:
            asset = Asset.resolve_symbol(symbol)
            return lambda value: asset(amount=Asset.float_to_nai_int(value, asset))

        super().__init__(
            items=[SelectItem(_asset_factory(symbol), symbol) for symbol in ["HIVE", "HBD"]],
            list_mount="ViewBag",
            placeholder="Select currency",
            selected=1,
        )


class TransferToAccount(CartBasedScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f2", "add_to_cart", "Add to cart"),
        Binding("f5", "fast_broadcast", "Fast broadcast"),
        Binding("f10", "finalize", "Finalize transaction"),
    ]

    def __init__(self) -> None:
        super().__init__()

        self.__to_input = Input(placeholder="e.g.: some-account")
        self.__amount_input = Input(placeholder="e.g.: 5.000")
        self.__memo_input = Input(placeholder="e.g.: For the coffee!")
        self.__currency_selector = CurrencySelector()

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Transfer to account")
            with Body():
                yield Static("from", classes="label")
                yield EllipsedStatic(str(self.app.world.profile_data.working_account.name), id_="from-label")
                yield PlaceTaker()
                yield Static("to", classes="label")
                yield self.__to_input
                yield Static("amount", classes="label")
                yield self.__amount_input
                yield self.__currency_selector
                yield Static("memo", classes="label")
                yield self.__memo_input

    def on_activate_succeeded(self) -> None:
        self.__fast_broadcast()

    def action_finalize(self) -> None:
        if self.__add_to_cart():
            self.app.switch_screen(TransactionSummary())
            self.app.push_screen_at(-1, Cart())

    def action_add_to_cart(self) -> None:
        if self.__add_to_cart():
            self.app.pop_screen()

    def action_fast_broadcast(self) -> None:
        if not self.__create_operation():  # For faster validation feedback to the user
            return

        if not self.app.world.app_state.is_active():
            self.app.push_screen(Activate())
            return

        self.__fast_broadcast()

    def __fast_broadcast(self) -> None:
        if operation := self.__create_operation():
            # TODO: Implement this action
            self.app.pop_screen()
            Notification(
                f"Operation `{operation.__class__.__name__}` broadcast succesfully.", category="success"
            ).show()

    def __create_operation(self) -> TransferOperation | None:
        """
        Collects data from the screen and creates a new operation based on it.
        :return: Operation if the operation is valid, None otherwise.
        """

        try:
            return TransferOperation(
                from_=str(self.app.world.profile_data.working_account.name),
                to=self.__to_input.value,
                amount=self.__currency_selector.selected.value(float(self.__amount_input.value)),
                memo=self.__memo_input.value,
            )
        except ValidationError as error:
            Notification(f"Operation failed the validation process.\n{error}", category="error").show()
            return None

    def __add_to_cart(self) -> bool:
        """
        Creates a new operation and adds it to the cart.
        :return: True if the operation was added to the cart successfully, False otherwise.
        """
        operation = self.__create_operation()
        if not operation:
            return False

        self.app.world.profile_data.cart.append(operation)
        self.app.world.update_reactive("profile_data")
        return True
