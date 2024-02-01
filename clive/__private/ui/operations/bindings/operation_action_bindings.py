from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import ValidationError
from textual.binding import Binding

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.core import iwax
from clive.__private.core.keys.key_manager import KeyNotFoundError
from clive.__private.ui.operations.cart import Cart
from clive.__private.ui.transaction_summary import TransactionSummaryFromCart
from clive.__private.ui.widgets.clive_screen import CliveScreen
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.inputs.clive_validated_input import (
    CliveValidatedInputError,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from clive.__private.core.keys import PublicKeyAliased
    from clive.models import Operation


class _NotImplemented:
    """Used to indicate that a method hasn't been implemented."""


class OperationActionBindings(CliveWidget, AbstractClassMessagePump):
    """Class to provide access to methods related with operations to not just screens."""

    BINDINGS = [
        Binding("f2", "add_to_cart", "Add to cart"),
        Binding("f5", "fast_broadcast", "Fast broadcast"),
        Binding("f10", "finalize", "Finalize transaction"),
    ]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Multiple inheritance friendly, passes arguments to next object in MRO.
        super().__init__(*args, **kwargs)

        self.__check_if_correctly_implemented()

    def _create_operation(self) -> Operation | None | _NotImplemented:
        """Should return a new operation based on the data from screen or None."""
        return _NotImplemented()

    def _create_operations(self) -> list[Operation] | None | _NotImplemented:
        """Should return a list of operations based on the data from screen or None."""
        return _NotImplemented()

    def _validate_and_notify(
        self, create_one_many_operations_cb: Callable[[], Operation | list[Operation] | None | _NotImplemented]
    ) -> list[Operation] | None:
        """
        Validates operations from callback result. If any of them is invalid, notifies the user and returns None.

        First it checks for any unhandled ValidationError (which may lead to app crash) from pydantic
        and then performs a wax validation.

        Args:
        ----
        create_one_many_operations_cb: A callback that returns either a single operation or a list of operations.
            It can also return None if the operation(s) couldn't be created. This means that the validation process
            is done earlier and here it will be skipped.
        """
        validation_failed_message = "Operation failed the validation process."

        try:
            result = create_one_many_operations_cb()
        except CliveValidatedInputError as error:
            self.notify(str(error), severity="error")
            return None
        except ValidationError as error:
            self.notify(f"{validation_failed_message}\n{error}", severity="error")
            return None

        if isinstance(result, _NotImplemented):
            return None

        if result is None:
            return None

        operations = result if isinstance(result, list) else [result]

        try:
            for operation in operations:
                iwax.validate_operation(operation)
        except iwax.WaxOperationFailedError as error:
            self.notify(f"{validation_failed_message}\n{error}", severity="error")
            return None

        return operations

    def create_operation(self) -> Operation | None:
        result = self._validate_and_notify(self._create_operation)
        return result[0] if result else None

    def create_operations(self) -> list[Operation] | None:
        return self._validate_and_notify(self._create_operations)

    def action_finalize(self) -> None:
        if self._add_to_cart():
            self.app.switch_screen(TransactionSummaryFromCart())
            self.app.push_screen_at(-1, Cart())

    def action_add_to_cart(self) -> None:
        if self._add_to_cart():
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

        operations = self.ensure_operations_list()

        if not key or not operations:
            return

        wrapper = await self.app.world.commands.fast_broadcast(content=operations, sign_with=key)
        if not wrapper.success:
            return

        transaction = wrapper.result_or_raise
        transaction_id = transaction.calculate_transaction_id()

        self.app.pop_screen_until("Operations")

        self.notify(f"Transaction with ID '{transaction_id}' successfully broadcasted!")

    def _add_to_cart(self) -> bool:
        """
        Create a new operation and adds it to the cart.

        Returns
        -------
        True if the operation was added to the cart successfully, False otherwise.
        """
        operations = self.ensure_operations_list()
        if not operations:
            return False

        self.app.world.profile_data.cart.extend(operations)
        self.app.trigger_profile_data_watchers()
        return True

    def ensure_operations_list(self) -> list[Operation]:
        operation = self.create_operation()
        if operation is not None:
            return [operation]

        operations = self.create_operations()
        if operations is not None:
            return operations
        return []

    def __check_if_correctly_implemented(self) -> None:
        with self.app.suppressed_notifications():
            try:
                create_operation_missing = isinstance(self._create_operation(), _NotImplemented)
            except Exception:  # noqa: BLE001
                create_operation_missing = False

            try:
                create_operations_missing = isinstance(self._create_operations(), _NotImplemented)
            except Exception:  # noqa: BLE001
                create_operations_missing = False

        if sum([create_operation_missing, create_operations_missing]) != 1:
            raise RuntimeError("One and only one of `_create_operation` or `_create_operations` should be implemented.")
