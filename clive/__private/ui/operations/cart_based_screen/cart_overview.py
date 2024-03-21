from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Container, Grid
from textual.widgets import Static

from clive.__private.core.formatters.humanize import humanize_operation_name
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.dynamic_label import DynamicLabel
from clive.__private.ui.widgets.scrolling import ScrollablePartFocusable
from clive.models import Asset

if TYPE_CHECKING:
    from textual.app import ComposeResult

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
        super().__init__(self.app.world, "profile_data", self.__get_cart_item_count)

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

    def compose(self) -> ComposeResult:
        with Resources():
            yield Static("RC:")
            yield DynamicLabel(self.app.world, "profile_data", self.__get_rc)
            yield Static("HIVE balance:")
            yield DynamicLabel(self.app.world, "profile_data", self.__get_hive_balance)
            yield Static("HBD balance:")
            yield DynamicLabel(self.app.world, "profile_data", self.__get_hbd_balance)
        with CartInfoContainer():
            yield CartItemsAmount()
            with self.__cart_items_container:
                yield from self.__create_cart_items()

    def on_mount(self) -> None:
        self.watch(self.app.world, "profile_data", callback=self.__sync_cart_items)

    def __sync_cart_items(self, _: ProfileData) -> None:
        with self.app.batch_update():
            self.__cart_items_container.query(CartItem).remove()
            new_cart_items = self.__create_cart_items()
            self.__cart_items_container.mount(*new_cart_items)

    @staticmethod
    def __get_rc(profile_data: ProfileData) -> str:
        return f"{profile_data.working_account.data.rc_manabar.percentage:.2f}%"

    @staticmethod
    def __get_hive_balance(profile_data: ProfileData) -> str:
        return Asset.to_legacy(profile_data.working_account.data.hive_balance)

    @staticmethod
    def __get_hbd_balance(profile_data: ProfileData) -> str:
        return Asset.to_legacy(profile_data.working_account.data.hbd_balance)

    def __create_cart_items(self) -> list[CartItem]:
        return [CartItem(index + 1, operation) for index, operation in enumerate(self.app.world.profile_data.cart)]
