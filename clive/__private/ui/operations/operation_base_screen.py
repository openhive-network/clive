from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from pydantic import ValidationError
from textual.binding import Binding

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.core import iwax
from clive.__private.core.keys.key_manager import KeyNotFoundError
from clive.__private.ui.operations.cart import Cart
from clive.__private.ui.operations.cart_based_screen.cart_based_screen import CartBasedScreen
from clive.__private.ui.operations.transaction_summary import TransactionSummary
from clive.__private.ui.widgets.clive_screen import CliveScreen

if TYPE_CHECKING:
    from clive.__private.core.keys import PublicKeyAliased
    from clive.models import Operation


class OperationBaseScreen(CartBasedScreen, AbstractClassMessagePump):
    """Base class for all screens that represent operations."""

    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f2", "add_to_cart", "Add to cart"),
        Binding("f5", "fast_broadcast", "Fast broadcast"),
        Binding("f10", "finalize", "Finalize transaction"),
    ]

    @abstractmethod
    def _create_operation(self) -> Operation | None:
        """Should return a new operation based on the data from screen."""

    def create_operation(self) -> Operation | None:
        """
        Tries to create a new operation.

        Returns
        -------
            Operation if the operation is valid, None otherwise.
        """
        try:
            operation = self._create_operation()
            if operation is None:
                return None
            iwax.validate_operation(operation)

            return operation  # noqa: TRY300
        except (ValidationError, iwax.WaxOperationFailedError) as error:
            self.notify(f"Operation failed the validation process.\n{error}", severity="error")
            return None

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

        self.__fast_broadcast()

    @CliveScreen.try_again_after_activation()
    def __fast_broadcast(self) -> None:
        def get_key() -> PublicKeyAliased | None:
            try:
                return self.app.world.profile_data.working_account.keys.first
            except KeyNotFoundError:
                self.notify("No keys found for the working account.", severity="error")
                return None

        key = get_key()
        operation = self.create_operation()

        if not key or not operation:
            return

        if not self.app.world.commands.fast_broadcast(operation=operation, sign_with=key).success:
            return

        self.app.pop_screen()
        self.notify(f"Operation `{operation.__class__.__name__}` broadcast successfully.")

    def __add_to_cart(self) -> bool:
        """
        Create a new operation and adds it to the cart.

        Returns
        -------
        True if the operation was added to the cart successfully, False otherwise.
        """
        operation = self.create_operation()
        if not operation:
            return False

        self.app.world.profile_data.cart.append(operation)
        self.app.world.update_reactive("profile_data")
        return True
