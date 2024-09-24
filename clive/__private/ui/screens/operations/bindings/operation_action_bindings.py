from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any, ClassVar, Final

from pydantic import ValidationError
from textual.binding import Binding
from textual.css.query import NoMatches

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.core import iwax
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.screens.transaction_summary.transaction_summary import TransactionSummary
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.clive_validated_input import (
    CliveValidatedInput,
    CliveValidatedInputError,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from clive.__private.core.accounts.accounts import Account
    from clive.__private.models.schemas import OperationUnion

INVALID_OPERATION_WARNING: Final[str] = "Can't proceed with empty or invalid operation(s)!"


class _NotImplemented:
    """Used to indicate that a method hasn't been implemented."""


class OperationActionBindings(CliveWidget, AbstractClassMessagePump):
    """Class to provide access to methods related with operations to not just screens."""

    BINDINGS = [
        Binding("f2", "add_to_cart", "Add to cart"),
        Binding("f6", "transaction_summary", "Transaction summary"),
    ]

    ALLOW_THE_SAME_OPERATION_IN_CART_MULTIPLE_TIMES: ClassVar[bool] = True
    ADD_TO_CART_POP_SCREEN_MODE: bool = False

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

    def action_transaction_summary(self) -> None:
        if self._add_to_cart():
            self._add_account_to_known_after_action()
            self.app.switch_screen(TransactionSummary())

    def action_add_to_cart(self) -> None:
        if self._add_to_cart():
            self._add_account_to_known_after_action()
            if self.ADD_TO_CART_POP_SCREEN_MODE:
                self.app.pop_screen()
            self._clear_inputs()

    def get_account_to_be_marked_as_known(self) -> str | Account | None:
        """
        Return the account (if overwritten) that should have been marked as known after action like add to cart.

        Notice:
        _______
        If this method is not overridden, the account from the account name input (action receiver),
        will be marked as known.
        """
        return None

    def _add_to_cart(self) -> bool:
        """
        Create a new operation and adds it to the cart.

        Returns
        -------
        True if the operation was added to the cart successfully, False otherwise.
        """
        if not self.ALLOW_THE_SAME_OPERATION_IN_CART_MULTIPLE_TIMES:
            operation = self.create_operation()
            if operation is not None and operation in self.profile.cart:
                self.notify("Operation already in the cart", severity="error")
                return False

        operations = self.ensure_operations_list()
        if not operations:
            self.notify(INVALID_OPERATION_WARNING, severity="warning")
            return False

        self.profile.cart.extend(operations)
        self.app.trigger_profile_watchers()
        return True

    def _add_account_to_known_after_action(self) -> None:
        """Add account that is given via parameter. If not given - add all accounts from the account name inputs."""
        account = self.get_account_to_be_marked_as_known()

        if account is not None:
            if not self.profile.accounts.is_account_known(account):
                self.profile.accounts.known.add(account)
            return

        with contextlib.suppress(NoMatches):
            self.query_one(AccountNameInput).add_account_to_known()

    def _clear_inputs(self) -> None:
        inputs = self.query(CliveValidatedInput)  # type: ignore[type-abstract]
        for widget in inputs:
            widget.input.clear()
            widget.clear_validation()

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
