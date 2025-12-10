from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, cast, override

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import CLINoChangesTransactionError, CLIPrettyError
from clive.__private.core.operations.authority_operations import (
    AuthorityAlreadyExistsError,
    AuthorityNotFoundError,
)
from clive.__private.core.operations.authority_operations import (
    add_account as _add_account,
)
from clive.__private.core.operations.authority_operations import (
    add_key as _add_key,
)
from clive.__private.core.operations.authority_operations import (
    modify_account as _modify_account,
)
from clive.__private.core.operations.authority_operations import (
    modify_key as _modify_key,
)
from clive.__private.core.operations.authority_operations import (
    remove_account as _remove_account,
)
from clive.__private.core.operations.authority_operations import (
    remove_key as _remove_key,
)
from clive.__private.core.operations.authority_operations import (
    set_threshold as _set_threshold,
)
from clive.__private.models.schemas import AccountUpdate2Operation, Authority, PublicKey

if TYPE_CHECKING:
    from clive.__private.cli.types import AccountUpdateFunction, AuthorityUpdateFunction, ComposeTransaction
    from clive.__private.core.types import AuthorityLevelRegular
    from clive.__private.models.schemas import Account


@dataclass(kw_only=True)
class ProcessAccountUpdate(OperationCommand):
    account_name: str
    _account: Account = field(init=False)
    _callbacks: list[AccountUpdateFunction] = field(default_factory=list)

    @override
    async def fetch_data(self) -> None:
        accounts = (await self.world.commands.find_accounts(accounts=[self.account_name])).result_or_raise
        self._account = accounts[0]

    @override
    async def validate(self) -> None:
        if len(self._callbacks) == 0:
            raise CLINoChangesTransactionError
        await super().validate()

    async def _create_operations(self) -> ComposeTransaction:
        previous_state = self.__create_operation_from_stored_state(self._account)
        modified_state = deepcopy(previous_state)

        for callback in self._callbacks:
            modified_state = callback(modified_state)

        yield self.__skip_untouched_fields(previous_state, modified_state)

    def add_callback(self, callback: AccountUpdateFunction) -> None:
        self._callbacks.append(callback)

    def modify_common_options(
        self,
        *,
        sign_with: str | None = None,
        autosign: bool | None = None,
        broadcast: bool | None = None,
        save_file: str | None = None,
    ) -> None:
        is_sign_given = sign_with is not None
        is_broadcast_given = broadcast is not None
        is_save_file_given = save_file is not None
        is_autosign_given = autosign is not None

        if is_sign_given:
            self.sign_with = sign_with

        if is_broadcast_given:
            self.broadcast = cast("bool", broadcast)

        if is_save_file_given:
            self.save_file = save_file

        if is_autosign_given:
            self.autosign = cast("bool", autosign)

    def __skip_untouched_fields(
        self, previous_state: AccountUpdate2Operation, modified_state: AccountUpdate2Operation
    ) -> AccountUpdate2Operation:
        return AccountUpdate2Operation(
            account=previous_state.account,
            owner=modified_state.owner if modified_state.owner != previous_state.owner else None,
            active=modified_state.active if modified_state.active != previous_state.active else None,
            posting=modified_state.posting if modified_state.posting != previous_state.posting else None,
            memo_key=modified_state.memo_key if modified_state.memo_key != previous_state.memo_key else None,
            json_metadata="",
            posting_json_metadata="",
            extensions=[],
        )

    def __create_operation_from_stored_state(self, account: Account) -> AccountUpdate2Operation:
        return AccountUpdate2Operation(
            account=account.name,
            owner=account.owner,
            active=account.active,
            posting=account.posting,
            memo_key=account.memo_key,
            json_metadata="",
            posting_json_metadata="",
            extensions=[],
        )


# Wrapper functions that convert core exceptions to CLI-friendly errors


def add_account(auth: Authority, account: str, weight: int) -> Authority:
    """Add an account to the authority."""
    try:
        return _add_account(auth, account, weight)
    except AuthorityAlreadyExistsError:
        raise CLIPrettyError(f"Account {account} is current account authority") from None


def add_key(auth: Authority, key: str, weight: int) -> Authority:
    """Add a key to the authority."""
    try:
        return _add_key(auth, key, weight)
    except AuthorityAlreadyExistsError:
        raise CLIPrettyError(f"Key {key} is current key authority") from None


def remove_account(auth: Authority, account: str) -> Authority:
    """Remove an account from the authority."""
    try:
        return _remove_account(auth, account)
    except AuthorityNotFoundError:
        raise CLIPrettyError(f"Account {account} is not current account authority") from None


def remove_key(auth: Authority, key: str) -> Authority:
    """Remove a key from the authority."""
    try:
        return _remove_key(auth, key)
    except AuthorityNotFoundError:
        raise CLIPrettyError(f"Key {key} is not current key authority") from None


def modify_account(auth: Authority, account: str, weight: int) -> Authority:
    """Modify the weight of an account in the authority."""
    try:
        return _modify_account(auth, account, weight)
    except (AuthorityAlreadyExistsError, AuthorityNotFoundError) as e:
        # Re-raise as CLIPrettyError with appropriate message
        if isinstance(e, AuthorityNotFoundError):
            raise CLIPrettyError(f"Account {account} is not current account authority") from None
        raise CLIPrettyError(f"Account {account} is current account authority") from None


def modify_key(auth: Authority, key: str, weight: int) -> Authority:
    """Modify the weight of a key in the authority."""
    try:
        return _modify_key(auth, key, weight)
    except (AuthorityAlreadyExistsError, AuthorityNotFoundError) as e:
        # Re-raise as CLIPrettyError with appropriate message
        if isinstance(e, AuthorityNotFoundError):
            raise CLIPrettyError(f"Key {key} is not current key authority") from None
        raise CLIPrettyError(f"Key {key} is current key authority") from None


def set_threshold(auth: Authority, threshold: int) -> Authority:
    """Set the weight threshold for an authority."""
    return _set_threshold(auth, threshold)


def set_memo_key(operation: AccountUpdate2Operation, key: str) -> AccountUpdate2Operation:
    operation.memo_key = PublicKey(key)
    return operation


def update_authority(
    operation: AccountUpdate2Operation, attribute: AuthorityLevelRegular, callback: AuthorityUpdateFunction
) -> AccountUpdate2Operation:
    auth_attribute = getattr(operation, attribute)
    if not auth_attribute:
        auth_attribute = Authority(weight_threshold=1, account_auths=[], key_auths=[])
        setattr(operation, attribute, auth_attribute)
    setattr(operation, attribute, callback(auth_attribute))
    return operation
