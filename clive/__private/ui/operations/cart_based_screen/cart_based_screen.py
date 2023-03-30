from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

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


class CartBasedScreen(BaseScreen, AbstractClassMessagePump):
    def create_main_panel(self) -> ComposeResult:
        with Horizontal():
            with LeftContainer():
                yield from self.create_left_panel()
            with RightContainer():
                yield CartOverview()

    @abstractmethod
    def create_left_panel(self) -> ComposeResult:
        """Should yield the left panel widgets."""
