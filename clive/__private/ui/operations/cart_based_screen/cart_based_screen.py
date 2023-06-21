from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from textual.containers import Container, Horizontal

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.ui.activate.activate import Activate
from clive.__private.ui.operations.cart import Cart
from clive.__private.ui.operations.cart_based_screen.cart_overview import CartOverview
from clive.__private.ui.operations.tranaction_summary import TransactionSummary
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.widgets.notification import Notification

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models import Operation


class LeftContainer(Container):
    """A container that holds the left side of the screen."""


class RightContainer(Container):
    """A container that holds the right side of the screen."""


class CartBasedScreen(BaseScreen, AbstractClassMessagePump):
    """Base class for all screens which all Operations screen"""

    def create_main_panel(self) -> ComposeResult:
        with Horizontal():
            with LeftContainer():
                yield from self.create_left_panel()
            with RightContainer():
                yield CartOverview()

    @abstractmethod
    def create_left_panel(self) -> ComposeResult:
        """Should yield the left panel widgets."""

    @abstractmethod
    def create_operation(self) -> Operation | None:
        """
        Collects data from the screen and creates a new operation based on it.
        :return: Operation if the operation is valid, None otherwise.
        """

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
        if not self.create_operation():  # For faster validation feedback to the user
            return

        if not self.app.world.app_state.is_active():
            self.app.push_screen(Activate())
            return

        self.__fast_broadcast()

    def __fast_broadcast(self) -> None:
        if operation := self.create_operation():
            self.app.world.commands.fast_broadcast(
                operation=operation, sign_with=self.app.world.profile_data.working_account.keys[0]
            )
            self.app.pop_screen()
            Notification(
                f"Operation `{operation.__class__.__name__}` broadcast succesfully.", category="success"
            ).show()

    def __add_to_cart(self) -> bool:
        """
        Creates a new operation and adds it to the cart.
        :return: True if the operation was added to the cart successfully, False otherwise.
        """
        operation = self.create_operation()
        if not operation:
            return False

        self.app.world.profile_data.cart.append(operation)
        self.app.world.update_reactive("profile_data")
        return True
