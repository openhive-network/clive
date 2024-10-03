from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any, ClassVar, Final, Literal

from pydantic import ValidationError
from textual.binding import Binding
from textual.css.query import NoMatches

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.core import iwax
from clive.__private.core.keys.key_manager import KeyNotFoundError
from clive.__private.ui.clive_screen import CliveScreen
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.dialogs.confirm_action_dialog_with_known_exchange import ConfirmActionDialogWithKnownExchange
from clive.__private.ui.screens.transaction_summary import TransactionSummary
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.clive_validated_input import (
    CliveValidatedInputError,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from clive.__private.core.accounts.accounts import Account
    from clive.__private.core.keys import PublicKeyAliased
    from clive.__private.models.schemas import OperationUnion

INVALID_OPERATION_WARNING: Final[str] = "Can't proceed with empty or invalid operation(s)!"


class _NotImplemented:
    """Used to indicate that a method hasn't been implemented."""


class OperationActionBindings(CliveWidget, AbstractClassMessagePump):
    """Class to provide access to methods related with operations to not just screens."""

    BINDINGS = [
        Binding("f2", "add_to_cart", "Add to cart"),
        Binding("f5", "fast_broadcast", "Fast broadcast"),
        Binding("f6", "finalize_transaction", "Finalize transaction"),
    ]
    ALLOW_THE_SAME_OPERATION_IN_CART_MULTIPLE_TIMES: ClassVar[bool] = True
    ADD_TO_CART_POP_SCREEN_MODE: Literal["pop", "until_operations_or_dashboard"] = "pop"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Multiple inheritance friendly, passes arguments to next object in MRO.
        super().__init__(*args, **kwargs)

        self.__check_if_correctly_implemented()

    def _create_operation(self) -> OperationUnion | None | _NotImplemented:
        """Return a new operation based on the data from screen or None."""
        return _NotImplemented()

    def _create_operations(self) -> list[OperationUnion] | None | _NotImplemented:
        """Return a list of operations based on the data from screen or None."""
        return _NotImplemented()

    def _validate_and_notify(
        self,
        create_one_many_operations_cb: Callable[[], OperationUnion | list[OperationUnion] | None | _NotImplemented],
    ) -> list[OperationUnion] | None:
        """
        Validate operations from callback result. If any of them is invalid, notifies the user and returns None.

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

    def create_operation(self) -> OperationUnion | None:
        result = self._validate_and_notify(self._create_operation)
        return result[0] if result else None

    def create_operations(self) -> list[OperationUnion] | None:
        return self._validate_and_notify(self._create_operations)

    async def action_finalize_transaction(self) -> None:
        async def finalize() -> None:
            if self._add_to_cart():
                self._add_account_to_known_after_action()
                transaction = (
                    (await self.commands.build_transaction(content=self.profile.cart)).result_or_raise
                    if self.profile.cart
                    else None
                )
                await self.app.switch_screen(TransactionSummary(transaction))

        async def finalize_cb(confirm: bool | None) -> None:
            if confirm:
                await finalize()

        if not self._can_proceed_operation():  # For faster validation feedback to the user
            return

        if self._check_is_known_exchange_in_input():
            await self.app.push_screen(ConfirmActionDialogWithKnownExchange(), finalize_cb)
        else:
            await finalize()

    def action_add_to_cart(self) -> None:
        def add_to_cart() -> None:
            if self._add_to_cart():
                self._add_account_to_known_after_action()
                self._pop_screen_on_successfully_added_to_cart()

        def add_to_cart_cb(confirm: bool | None) -> None:
            if confirm:
                add_to_cart()

        if not self._can_proceed_operation():  # For faster validation feedback to the user
            return

        if self._check_is_known_exchange_in_input():
            self.app.push_screen(ConfirmActionDialogWithKnownExchange(), add_to_cart_cb)
        else:
            add_to_cart()

    def _pop_screen_on_successfully_added_to_cart(self) -> None:
        if self.ADD_TO_CART_POP_SCREEN_MODE == "pop":
            self.app.pop_screen()
        elif self.ADD_TO_CART_POP_SCREEN_MODE == "until_operations_or_dashboard":
            self._pop_screen_until_operations_or_dashboard()

    async def action_fast_broadcast(self) -> None:
        async def fast_broadcast_cb(confirm: bool | None) -> None:
            if confirm:
                await self.__fast_broadcast()

        if not self._can_proceed_operation():  # For faster validation feedback to the user
            return

        if self._check_is_known_exchange_in_input():
            await self.app.push_screen(ConfirmActionDialogWithKnownExchange(), fast_broadcast_cb)
        else:
            await self.__fast_broadcast()

    def get_account_to_be_marked_as_known(self) -> str | Account | None:
        """
        Return the account (if overwritten) that should have been marked as known after action like add to cart.

        Notice:
        _______
        If this method is not overridden, the account from the account name input (action receiver),
        will be marked as known.
        """
        return None

    def check_is_known_exchange_in_input(self) -> bool | None:
        """
        Check if the account name input (action receiver) is a known exchange account (if overwritten).

        Notice:
        _______
        If this method is not overridden, the account from the account name input (action receiver),
        will be checked for being a known exchange.
        """
        return None

    @CliveScreen.try_again_after_unlock
    async def __fast_broadcast(self) -> None:
        def get_key() -> PublicKeyAliased | None:
            try:
                return self.profile.keys.first
            except KeyNotFoundError:
                self.notify("No keys found for the working account.", severity="error")
                return None

        key = get_key()

        operations = self.ensure_operations_list()

        if not key or not operations:
            return

        wrapper = await self.commands.fast_broadcast(content=operations, sign_with=key)
        if not wrapper.success:
            return

        transaction = wrapper.result_or_raise
        transaction_id = transaction.calculate_transaction_id()

        self._add_account_to_known_after_action()
        self._pop_screen_until_operations_or_dashboard()
        self.notify(f"Transaction with ID '{transaction_id}' successfully broadcasted!")

    def _can_proceed_operation(self) -> bool:
        if not self.create_operation() and not self.create_operations():
            self.notify(INVALID_OPERATION_WARNING, severity="warning")
            return False
        return True

    def _add_to_cart(self) -> bool:
        """
        Create a new operation and adds it to the cart.

        Returns
        -------
        True if the operation was added to the cart successfully, False otherwise.
        """
        operations = self.ensure_operations_list()
        assert operations, "when calling '_add_to_cart', operations must not be empty"

        if not self.ALLOW_THE_SAME_OPERATION_IN_CART_MULTIPLE_TIMES:
            for operation in operations:
                if operation in self.profile.cart:
                    self.notify("Operation already in the cart", severity="error")
                    return False

        self.profile.cart.extend(operations)
        self.app.trigger_profile_watchers()
        return True

    def _check_is_known_exchange_in_input(self) -> bool:
        is_known_exchange_in_input = self.check_is_known_exchange_in_input()

        if is_known_exchange_in_input is not None:
            return is_known_exchange_in_input

        with contextlib.suppress(NoMatches):
            return self.query_one(AccountNameInput).value_raw in self.world.known_exchanges

        return False

    def _add_account_to_known_after_action(self) -> None:
        """Add account that is given via parameter. If not given - add all accounts from the account name inputs."""
        account = self.get_account_to_be_marked_as_known()

        if account is not None:
            if not self.profile.accounts.is_account_known(account):
                self.profile.accounts.known.add(account)
            return

        with contextlib.suppress(NoMatches):
            self.query_exactly_one(AccountNameInput).add_account_to_known()

    def ensure_operations_list(self) -> list[OperationUnion]:
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

    def _pop_screen_until_operations_or_dashboard(self) -> None:
        from clive.__private.ui.screens.dashboard import Dashboard
        from clive.__private.ui.screens.operations import Operations

        self.app.pop_screen_until(Operations, Dashboard)
