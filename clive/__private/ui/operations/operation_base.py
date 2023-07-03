from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from pydantic import ValidationError
from textual.binding import Binding

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.ui.activate.activate import Activate
from clive.__private.ui.operations.cart import Cart
from clive.__private.ui.operations.cart_based_screen.cart_based_screen import CartBasedScreen
from clive.__private.ui.operations.tranaction_summary import TransactionSummary
from clive.__private.ui.widgets.notification import Notification

if TYPE_CHECKING:
    from clive.models import Operation


class OperationBase(CartBasedScreen, AbstractClassMessagePump):
    """Base class for all screens that represent operations"""

    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f2", "add_to_cart", "Add to cart"),
        Binding("f5", "fast_broadcast", "Fast broadcast"),
        Binding("f10", "finalize", "Finalize transaction"),
    ]

    @abstractmethod
    def _create_operation(self) -> Operation | None:
        """Should return a new operation based on the data from screen"""

    def create_operation(self) -> Operation | None:
        """
        Tries to create a new operation

        Returns:
            Operation if the operation is valid, None otherwise.
        """
        try:
            return self._create_operation()
        except ValidationError as error:
            Notification(f"Operation failed the validation process.\n{error}", category="error").show()
            return None

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

    @staticmethod
    def _split_auths_fields(auths: str) -> list[tuple[str, int]]:
        """To create valid format of auths like key_auths, to create pydantic operation model"""
        valid_auths_format = []

        split_auths = auths.split(";")
        for pair in split_auths:
            string_part, number = pair.split(",")

            string_part = string_part.strip()
            valid_auths_format.append((string_part, int(number)))

        return valid_auths_format
