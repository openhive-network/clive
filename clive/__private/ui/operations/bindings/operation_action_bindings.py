from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import ValidationError
from textual.binding import Binding

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.core import iwax
from clive.__private.core.keys.key_manager import KeyNotFoundError
from clive.__private.ui.operations.cart import Cart
from clive.__private.ui.transaction_summary import TransactionSummaryFromCart
from clive.__private.ui.widgets.clive_screen import CliveScreen
from clive.__private.ui.widgets.clive_widget import CliveWidget

if TYPE_CHECKING:
    from clive.__private.core.keys import PublicKeyAliased
    from clive.models import Operation


class OperationActionBindings(CliveWidget, AbstractClassMessagePump):
    """Class to provide access to methods related with operations to not just screens."""

    BINDINGS = [
        Binding("f2", "add_to_cart", "Add to cart"),
        Binding("f5", "fast_broadcast", "Fast broadcast"),
        Binding("f10", "finalize", "Finalize transaction"),
    ]

    def _create_operation(self) -> Operation | None:
        """Should return a new operation based on the data from screen."""
        return None

    def _create_operations(self) -> list[Operation] | None:
        """Should return a list of operations based on the data from screen."""
        return None

    def _validate_and_notify(self, operations: list[Operation]) -> list[Operation] | None:
        """Validates the given operations. If any of them is invalid, notifies the user and returns None."""
        try:
            for operation in operations:
                iwax.validate_operation(operation)
        except (ValidationError, iwax.WaxOperationFailedError) as error:
            self.notify(f"Operation failed the validation process.\n{error}", severity="error")
            return None
        return operations

    def create_operation(self) -> Operation | None:
        operation = self._create_operation()
        if operation is None:
            return None
        result = self._validate_and_notify([operation])
        return result[0] if result else None

    def create_operations(self) -> list[Operation] | None:
        if self._create_operation() is not None:
            raise ValueError("This method should be used only when creating multiple operations.")

        operations = self._create_operations()
        if operations is None:
            return None

        return self._validate_and_notify(operations)

    def action_finalize(self) -> None:
        if self.__add_to_cart():
            self.app.switch_screen(TransactionSummaryFromCart())
            self.app.push_screen_at(-1, Cart())

    def action_add_to_cart(self) -> None:
        if self.__add_to_cart():
            self.app.pop_screen()

    async def action_fast_broadcast(self) -> None:
        if not self.create_operation() and not self.create_operations():  # For faster validation feedback to the user
            return

        await self.__fast_broadcast()

    @CliveScreen.try_again_after_activation()
    async def __fast_broadcast(self) -> None:
        def get_key() -> PublicKeyAliased | None:
            try:
                return self.app.world.profile_data.working_account.keys.first
            except KeyNotFoundError:
                self.notify("No keys found for the working account.", severity="error")
                return None

        key = get_key()

        operation = self.create_operation()
        operations = [operation] if operation else self.create_operations()

        if not key or not operations:
            return

        if not (await self.app.world.commands.fast_broadcast(content=operations, sign_with=key)).success:
            return

        self.app.pop_screen_until("Operations")

        if len(operations) == 1:
            message = f"Operation `{operations[0].__class__.__name__}` broadcast successfully."
        else:
            message = (
                f"Operations `{[operation.__class__.__name__ for operation in operations]}` broadcast successfully."
            )

        self.notify(message)

    def __add_to_cart(self) -> bool:
        """
        Create a new operation and adds it to the cart.

        Returns
        -------
        True if the operation was added to the cart successfully, False otherwise.
        """
        operation = self.create_operation()
        operations = [operation] if operation else self.create_operations()

        if not operations:
            return False

        self.app.world.profile_data.cart.extend(operations)
        self.app.trigger_profile_data_watchers()
        return True
