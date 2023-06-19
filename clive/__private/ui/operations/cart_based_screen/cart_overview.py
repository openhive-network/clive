from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Container, Grid
from textual.widgets import Static

from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.dynamic_label import DynamicLabel
from clive.models import Asset

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.profile_data import ProfileData
    from clive.models import Operation


class Resources(Grid):
    """A grid that holds the resources info."""


class CartInfoContainer(Container):
    """A container that holds the label with amount of items and items itself."""


class CartItem(DynamicLabel):
    """Holds the cart item info."""

    def __init__(
        self, operation: Operation, *, prefix: str = "", id_: str | None = None, classes: str | None = None
    ) -> None:
        self._operation = operation
        super().__init__(
            self.app.world, "profile_data", self.__fetch_operation_info, prefix=prefix, id_=id_, classes=classes
        )

    def __fetch_operation_info(self, profile_data: ProfileData) -> str:
        if self._operation in profile_data.cart:
            idx = profile_data.cart.index(self._operation)
            return f"{idx + 1}. {self._operation.__class__.__name__} operation"
        self.add_class("deleted")
        self.remove()
        return ""


class CartItemsAmount(DynamicLabel):
    """Holds the cart items amount info."""

    def __init__(self) -> None:
        super().__init__(self.app.world, "profile_data", self.__get_cart_item_count)

    def __get_cart_item_count(self, profile_data: ProfileData) -> str:
        amount = len(profile_data.cart)
        if amount > 0:
            return f"{amount} OPERATIONS IN THE CART"
        return "CART IS EMPTY"


class CartItemsContainer(Container):
    """A container that holds the cart items."""


class CartOverview(CliveWidget):
    def __init__(self) -> None:
        super().__init__()

        self.__cart_items_container = CartItemsContainer()
        self.__current_cart_operations = self.__get_operations_from_cart()

    def compose(self) -> ComposeResult:
        with Resources():
            yield Static("Resource credits (RC):")
            yield DynamicLabel(self.app.world, "profile_data", self.__get_rc)
            yield Static("Enough RC for approx.:")
            yield Static("17 transfers")
            yield Static("HIVE balance:")
            yield DynamicLabel(self.app.world, "profile_data", self.__get_hive_balance)
            yield Static("HBD balance:")
            yield DynamicLabel(self.app.world, "profile_data", self.__get_hbd_balance)
        with CartInfoContainer():
            yield CartItemsAmount()
            with self.__cart_items_container:
                yield from self.__current_cart_operations
        yield Static()

    def on_mount(self) -> None:
        self.watch(self.app.world, "profile_data", callback=self.__sync_cart_items)

    def __sync_cart_items(self, _: ProfileData) -> None:
        current_ops = self.__get_operations_from_cart()

        def find_in_current_ops(op: CartItem) -> CartItem | None:
            for x in current_ops:
                # this custom comparator is because every time new objects are created
                # and shallow comparison returns false positive, that none of these
                # CartItem exists. Overriding __eq__ is invalid, because it breaks
                # textual internally. Comparison in this case has to be done on
                # Operation object, not CartItem
                if x._operation == op._operation:
                    return x
            return None

        for op in self.__current_cart_operations:
            nop = find_in_current_ops(op)
            if nop is not None:
                current_ops.remove(nop)
            else:
                op.add_class("deleted")
                op.remove()

        if len(current_ops) > 0:
            self.__cart_items_container.mount(*current_ops)
        self.__current_cart_operations = self.__get_operations_from_cart()

    @staticmethod
    def __get_rc(profile_data: ProfileData) -> str:
        return f"{profile_data.working_account.data.rc:.2f}%"

    @staticmethod
    def __get_hive_balance(profile_data: ProfileData) -> str:
        return Asset.to_legacy(profile_data.working_account.data.hive_balance)

    @staticmethod
    def __get_hbd_balance(profile_data: ProfileData) -> str:
        return Asset.to_legacy(profile_data.working_account.data.hive_dollars)

    def __get_operations_from_cart(self) -> list[CartItem]:
        return [CartItem(op) for op in self.app.world.profile_data.cart]
