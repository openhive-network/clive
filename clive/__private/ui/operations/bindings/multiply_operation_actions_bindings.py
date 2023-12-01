from __future__ import annotations

from abc import abstractmethod
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


class MultiplyOperationsActionsBindings(CliveWidget, AbstractClassMessagePump):
    """Bindings to broadcast or add to cart more than one operation."""

    BINDINGS = [
        Binding("f2", "add_to_cart", "Add to cart"),
        Binding("f5", "fast_broadcast", "Fast broadcast"),
        Binding("f10", "finalize", "Finalize transaction"),
    ]

    @abstractmethod
    def _create_operation(self) -> list[Operation] | None:
        """Should return a new operation based on the data from screen."""

    def create_operation(self) -> list[Operation] | None:
        """
        Tries to create a new operations.

        Returns
        -------
            List of Operation if the operation is valid, None otherwise.
        """
        try:
            operations = self._create_operation()
            if operations is None:
                return None

            for operation in operations:
                iwax.validate_operation(operation)

            return operations  # noqa: TRY300
        except (ValidationError, iwax.WaxOperationFailedError) as error:
            self.notify(f"Operation failed the validation process.\n{error}", severity="error")
            return None

    def action_finalize(self) -> None:
        if self.__add_to_cart():
            self.app.switch_screen(TransactionSummaryFromCart())
            self.app.push_screen_at(-1, Cart())

    def action_add_to_cart(self) -> None:
        if self.__add_to_cart():
            self.app.pop_screen()

    async def action_fast_broadcast(self) -> None:
        if not self.create_operation():  # For faster validation feedback to the user
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
        operations = self.create_operation()

        if not key or not operations:
            return

        for operation in operations:
            if not (await self.app.world.commands.fast_broadcast(content=operation, sign_with=key)).success:
                return

        self.app.pop_screen_until("Operations")
        self.notify("Operations modify votes for witnesses broadcast successfully.")

    def __add_to_cart(self) -> bool:
        """
        Create a new operations and add them to the cart.

        Returns
        -------
        True if the operations were added to the cart successfully, False otherwise.
        """
        operations = self.create_operation()
        if not operations:
            return False

        for operation in operations:
            self.app.world.profile_data.cart.append(operation)
        self.app.world.update_reactive("profile_data")
        return True
