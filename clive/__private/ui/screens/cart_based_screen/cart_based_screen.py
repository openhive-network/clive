from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from textual.containers import Container, Horizontal

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.screens.cart_based_screen.cart_overview import CartOverview

if TYPE_CHECKING:
    from textual.app import ComposeResult


class LeftContainer(Container):
    """A container that holds the left side of the screen."""


class RightContainer(Container):
    """A container that holds the right side of the screen."""


class CartBasedScreen(BaseScreen, AbstractClassMessagePump):
    """
    Base class for all screens that should show a brief cart summary.

    Attributes:
        CSS_PATH: CSS path to be applied to the screen.
    """

    CSS_PATH = [get_relative_css_path(__file__)]

    def create_main_panel(self) -> ComposeResult:
        with Horizontal():
            with LeftContainer():
                yield from self.create_left_panel()
            with RightContainer():
                yield CartOverview()

    @abstractmethod
    def create_left_panel(self) -> ComposeResult:
        """
        Yield the left panel widgets.

        Returns:
            The widgets to be displayed in the left panel.
        """
