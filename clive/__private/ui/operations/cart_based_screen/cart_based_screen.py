from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.containers import Container, Horizontal

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.ui.operations.cart_based_screen.cart_overview import CartOverview
from clive.__private.ui.shared.base_screen import BaseScreen

if TYPE_CHECKING:
    from textual.app import ComposeResult


class LeftContainer(Container):
    """A container that holds the left side of the screen."""


class RightContainer(Container):
    """A container that holds the right side of the screen."""


class CartBasedScreenOperation(BaseScreen, AbstractClassMessagePump):
    """Base class for Operations screen, which shows list of available operations"""

    def create_main_panel(self) -> ComposeResult:
        with Horizontal():
            with LeftContainer():
                yield from self.create_left_panel()
            with RightContainer():
                yield CartOverview()

    @abstractmethod
    def create_left_panel(self) -> ComposeResult:
        """Should yield the left panel widgets."""


class CartBasedScreenOperations(BaseScreen, AbstractClassMessagePump):
    """Base class for all screens which all Operations screen"""

    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f2", "add_to_cart", "Add to cart"),
        Binding("f5", "fast_broadcast", "Fast broadcast"),
        Binding("f10", "finalize", "Finalize transaction"),
    ]

    def create_main_panel(self) -> ComposeResult:
        with Horizontal():
            with LeftContainer():
                yield from self.create_left_panel()
            with RightContainer():
                yield CartOverview()

    @abstractmethod
    def create_left_panel(self) -> ComposeResult:
        """Should yield the left panel widgets."""
