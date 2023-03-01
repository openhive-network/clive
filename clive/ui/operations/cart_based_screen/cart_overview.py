from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Container, Grid
from textual.widget import Widget
from textual.widgets import Static

from clive.ui.widgets.dynamic_label import DynamicLabel

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.storage.mock_database import NodeData


class Resources(Grid):
    """A grid that holds the resources info."""


class CartInfoContainer(Container):
    """A container that holds the label with amount of items and items itself."""


class CartItem(Static):
    """Holds the cart item info."""


class CartItemsAmount(Static):
    """Holds the cart items amount info."""

    def __init__(self, amount: int) -> None:
        super().__init__(f"{amount} OPERATIONS IN THE CART" if amount > 0 else "CART IS EMPTY")


class CartItemsContainer(Container):
    """A container that holds the cart items."""


class CartOverview(Widget):
    def compose(self) -> ComposeResult:
        with Resources():
            yield Static("Resource credits (RC):")
            yield DynamicLabel(self.app, "node_data", self.__get_rc)
            yield Static("Enough RC for approx.:")
            yield Static("17 transfers")
            yield Static("HIVE balance:")
            yield DynamicLabel(self.app, "node_data", self.__get_hive_balance)
            yield Static("HBD balance:")
            yield DynamicLabel(self.app, "node_data", self.__get_hbd_balance)
        with CartInfoContainer():
            yield CartItemsAmount(len(self.__get_operations_from_cart()))
            with CartItemsContainer():
                yield from self.__get_operations_from_cart()
        yield Static()

    @staticmethod
    def __get_rc(node_data: NodeData) -> str:
        return f"{node_data.rc:.2f}%"

    @staticmethod
    def __get_hive_balance(node_data: NodeData) -> str:
        return f"{node_data.hive_balance:.2f} HIVE"

    @staticmethod
    def __get_hbd_balance(node_data: NodeData) -> str:
        return f"{node_data.hive_dollars:.2f} HBD"

    @staticmethod
    def __get_operations_from_cart() -> list[Static]:
        items_in_cart = 50

        return [CartItem(f"{i + 1}. Transfer to account") for i in range(items_in_cart)]
