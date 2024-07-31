from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Container, Grid, Horizontal
from textual.widgets import Static

from clive.__private.core.formatters.data_labels import MISSING_API_LABEL
from clive.__private.core.formatters.humanize import humanize_operation_name, humanize_percent
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.dynamic_label import DynamicLabel
from clive.__private.ui.widgets.scrolling import ScrollablePartFocusable
from clive.models import Asset

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.accounts.accounts import WorkingAccount
    from clive.__private.core.profile_data import ProfileData
    from clive.models import Operation


class Resources(Grid):
    """A grid that holds the resources info."""


class CartInfoContainer(Container):
    """A container that holds the label with amount of items and items itself."""


class CartItem(Static):
    """Holds the cart item info."""

    def __init__(self, index: int, operation: Operation) -> None:
        self._operation = operation
        super().__init__(f"{index}. {humanize_operation_name(operation)}")


class CartItemsAmount(DynamicLabel):
    """Holds the cart items amount info."""

    def __init__(self) -> None:
        super().__init__(self.world, "profile_data", self.__get_cart_item_count)

    def __get_cart_item_count(self, profile_data: ProfileData) -> str:
        amount = len(profile_data.cart)
        if amount > 0:
            return f"{amount} OPERATION{'S' if amount > 1 else ''} IN THE CART"
        return "CART IS EMPTY"


class CartItemsContainer(ScrollablePartFocusable):
    """A container that holds the cart items."""


class CartOverview(CliveWidget):
    def __init__(self) -> None:
        super().__init__()

        self.__cart_items_container = CartItemsContainer()
        self._rc_container = Horizontal(id="rc-container")

    @property
    def working_account(self) -> WorkingAccount:
        return self.profile_data.accounts.working

    def compose(self) -> ComposeResult:
        with Resources():
            with self._rc_container:
                yield Static("RC:")
                yield DynamicLabel(self.world, "profile_data", self.__get_rc)
            yield Static("HIVE balance:")
            yield DynamicLabel(self.world, "profile_data", self.__get_hive_balance)
            yield Static("HBD balance:")
            yield DynamicLabel(self.world, "profile_data", self.__get_hbd_balance)
        with CartInfoContainer():
            yield CartItemsAmount()
            with self.__cart_items_container:
                yield from self.__create_cart_items()

    def on_mount(self) -> None:
        self.watch(self.world, "profile_data", callback=self.__sync_cart_items)

    def __sync_cart_items(self, _: ProfileData) -> None:
        with self.app.batch_update():
            self.__cart_items_container.query(CartItem).remove()
            new_cart_items = self.__create_cart_items()
            self.__cart_items_container.mount(*new_cart_items)

    def __get_rc(self) -> str:
        self._set_rc_api_missing()
        if self.working_account.data.is_rc_api_missing:
            return MISSING_API_LABEL

        return humanize_percent(self.working_account.data.rc_manabar_ensure.percentage)

    def _set_rc_api_missing(self) -> None:
        if self.working_account.data.is_rc_api_missing:
            self._rc_container.tooltip = self.working_account.data.rc_manabar_ensure_missing_api.missing_api_text
            return

        self._rc_container.tooltip = None

    @staticmethod
    def __get_hive_balance(profile_data: ProfileData) -> str:
        return Asset.pretty_amount(profile_data.accounts.working.data.hive_balance)

    @staticmethod
    def __get_hbd_balance(profile_data: ProfileData) -> str:
        return Asset.pretty_amount(profile_data.accounts.working.data.hbd_balance)

    def __create_cart_items(self) -> list[CartItem]:
        return [CartItem(index + 1, operation) for index, operation in enumerate(self.profile_data.cart)]
