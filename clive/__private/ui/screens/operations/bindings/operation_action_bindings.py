from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any, ClassVar, Final

from textual import on
from textual.css.query import NoMatches

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.core import iwax
from clive.__private.models.schemas import ValidationError
from clive.__private.ui.bindings import CLIVE_PREDEFINED_BINDINGS
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.dialogs.confirm_action_dialog_with_known_exchange import ConfirmActionDialogWithKnownExchange
from clive.__private.ui.screens.transaction_summary import TransactionSummary
from clive.__private.ui.widgets.buttons import AddToCartButton, FinalizeTransactionButton
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.asset_amount_base_input import AssetAmountInput
from clive.__private.ui.widgets.inputs.clive_input import CliveInput
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
    """
    Class to provide access to methods related with operations to not just screens.

    Attributes:
        BINDINGS: A list of predefined bindings for operations.
        ALLOW_THE_SAME_OPERATION_IN_CART_MULTIPLE_TIMES: Whether operation with the same data can
            be added to the cart multiple times.

    Args:
        *args: Additional positional arguments.
        **kwargs: Additional keyword arguments.
    """

    BINDINGS = [
        CLIVE_PREDEFINED_BINDINGS.operations.add_to_cart.create(show=False),
        CLIVE_PREDEFINED_BINDINGS.operations.finalize_transaction.create(show=False),
    ]
    ALLOW_THE_SAME_OPERATION_IN_CART_MULTIPLE_TIMES: ClassVar[bool] = True

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Multiple inheritance friendly, passes arguments to next object in MRO.
        super().__init__(*args, **kwargs)

        self._check_if_correctly_implemented()

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

        First it checks for any unhandled ValidationError (which may lead to app crash) from schemas
        and then performs a wax validation.

        Args:
            create_one_many_operations_cb: A callback that returns either a single operation or a list of operations.
                It can also return None if the operation(s) couldn't be created. This means that the validation process
                is done earlier and here it will be skipped.

        Returns:
            A list of validated operations or None if validation failed.
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

    async def action_add_to_cart(self) -> None:
        await self._handle_add_to_cart_request()

    @on(AddToCartButton.Pressed)
    async def add_to_cart_by_button(self) -> None:
        await self._handle_add_to_cart_request()

    @on(CliveInput.Submitted)
    async def add_to_cart_with_event(self) -> None:
        await self._handle_add_to_cart_request()

    async def action_finalize_transaction(self) -> None:
        await self._handle_finalize_transaction_request()

    @on(FinalizeTransactionButton.Pressed)
    async def finalize_transaction_by_button(self) -> None:
        await self._handle_finalize_transaction_request()

    def check_is_known_exchange_in_input(self) -> bool | None:
        """
        Check if the account name input (action receiver) is a known exchange account (if overwritten).

        Notice:
            If this method is not overridden, the account from the account name input (action receiver),
                will be checked for being a known exchange.

        Returns:
            True if known exchange account is present in input. False if not.
        """
        return None

    def ensure_operations_list(self) -> list[OperationUnion]:
        operation = self.create_operation()
        if operation is not None:
            return [operation]

        operations = self.create_operations()
        if operations is not None:
            return operations
        return []

    def get_account_to_be_marked_as_known(self) -> str | Account | None:
        """
        Return the account (if overwritten) that should have been marked as known after action like add to cart.

        Notice:
            If this method is not overridden, the account from the account name input (action receiver),
                will be marked as known.

        Returns:
            The account name or account object that should be marked as known.
        """
        return None

    def _additional_actions_after_clearing_inputs(self) -> None:
        """Override it if you need any logic e.g. setting inputs to default value."""

    def _actions_after_clearing_inputs(self) -> None:
        # select default value in asset inputs
        for asset_input in self.query(AssetAmountInput):  # type: ignore[type-abstract]
            asset_input.select_asset(asset_input.default_asset_type)

        self._additional_actions_after_clearing_inputs()

    def _add_account_to_known_after_action(self) -> None:
        """Add account that is given via parameter. If not given - add all accounts from the account name inputs."""
        account = self.get_account_to_be_marked_as_known()

        if account is not None:
            if not self.profile.accounts.is_account_known(account):
                self.profile.accounts.known.add(account)
            return

        with contextlib.suppress(NoMatches):
            self.query_exactly_one(AccountNameInput).add_account_to_known()

    def _actions_after_adding_to_cart(self) -> None:
        """It's performing all actions needed after adding operation to cart."""
        if self.profile.transaction.is_signed:
            self.profile.transaction.unsign()
            self._send_cleared_signatures_notification()
        self.profile.transaction_file_path = None
        if self.profile.should_enable_known_accounts:
            self._add_account_to_known_after_action()
        self._clear_inputs()
        self._actions_after_clearing_inputs()

    def _add_to_cart(self, operations: list[OperationUnion], *, notify: bool = True) -> None:
        """Just adds given operations to cart."""
        self.profile.add_operation(*operations)
        self.app.trigger_profile_watchers()
        if notify:
            self.notify("The operation was added to the cart.")

    def _can_proceed_operation(self) -> bool:
        if not self.create_operation() and not self.create_operations():
            self.notify(INVALID_OPERATION_WARNING, severity="warning")
            return False
        return True

    def _check_if_correctly_implemented(self) -> None:
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

    def _check_is_known_exchange_in_input(self) -> bool:
        is_known_exchange_in_input = self.check_is_known_exchange_in_input()

        if is_known_exchange_in_input is not None:
            return is_known_exchange_in_input

        with contextlib.suppress(NoMatches):
            input_value = self.query_exactly_one(AccountNameInput).value_raw
            return input_value in self.world.known_exchanges

        return False

    def _clear_inputs(self) -> None:
        inputs = self.query(CliveValidatedInput)  # type: ignore[type-abstract]
        for widget in inputs:
            widget.clear_validation()

    async def _handle_add_to_cart_request(self) -> None:
        def add_operation_to_cart_and_perform_post_actions() -> None:
            self._add_to_cart(operations_to_add)
            self._actions_after_adding_to_cart()

        def cb(confirm: bool | None) -> None:  # noqa: FBT001
            if confirm:
                add_operation_to_cart_and_perform_post_actions()

        if not self._can_proceed_operation():  # For faster validation feedback to the user
            return

        operations_to_add = self.ensure_operations_list()
        assert operations_to_add, "when calling '_add_to_cart', operations must not be empty"

        if self._validate_operations_already_in_the_cart(operations_to_add):
            return

        if self._check_is_known_exchange_in_input():
            self.app.push_screen(ConfirmActionDialogWithKnownExchange(), cb)
        else:
            add_operation_to_cart_and_perform_post_actions()

    async def _handle_finalize_transaction_request(self) -> None:
        async def finalize_and_perform_post_actions() -> None:
            self._add_to_cart(operations_to_add, notify=False)
            self._actions_after_adding_to_cart()
            await self.commands.update_transaction_metadata(transaction=self.profile.transaction)
            await self.app.push_screen(TransactionSummary())

        async def cb(confirm: bool | None) -> None:  # noqa: FBT001
            if confirm:
                await finalize_and_perform_post_actions()

        if not self._can_proceed_operation():  # For faster validation feedback to the user
            return

        operations_to_add = self.ensure_operations_list()
        assert operations_to_add, "when calling '_add_to_cart', operations must not be empty"

        if self._validate_operations_already_in_the_cart(operations_to_add):
            return

        if self._check_is_known_exchange_in_input():
            await self.app.push_screen(ConfirmActionDialogWithKnownExchange(), cb)
        else:
            await finalize_and_perform_post_actions()

    def _send_cleared_signatures_notification(self) -> None:
        self.notify(
            "Transaction signatures were removed since you changed the transaction content.",
            severity="warning",
        )

    def _validate_operations_already_in_the_cart(self, operations: list[OperationUnion]) -> bool:
        if not self.ALLOW_THE_SAME_OPERATION_IN_CART_MULTIPLE_TIMES and any(
            operation in self.profile.transaction for operation in operations
        ):
            self.notify("Operation already in the cart", severity="error")
            return True
        return False
