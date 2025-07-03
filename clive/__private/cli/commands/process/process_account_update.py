from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.models.schemas import AccountName, AccountUpdate2Operation, Authority, HiveInt, PublicKey

if TYPE_CHECKING:
    from clive.__private.cli.types import (
        AccountUpdateFunction,
        AuthorityType,
        AuthorityUpdateFunction,
    )
    from clive.__private.models.schemas import Account


@dataclass(kw_only=True)
class ProcessAccountUpdate(OperationCommand):
    """
    Class to process account update operations.

    Args:
        account_name: The name of the account to update.
    """

    account_name: str
    _callbacks: list[AccountUpdateFunction] = field(default_factory=list)

    async def _create_operation(self) -> AccountUpdate2Operation:
        """
        Create an account update operation based on the current state of the account.

        Returns:
            AccountUpdate2Operation: The operation representing the account update.
        """
        accounts = (await self.world.commands.find_accounts(accounts=[self.account_name])).result_or_raise

        account = accounts[0]
        previous_state = self.__create_operation_from_stored_state(account)
        modified_state = deepcopy(previous_state)

        for callback in self._callbacks:
            modified_state = callback(modified_state)

        return self.__skip_untouched_fields(previous_state, modified_state)

    def add_callback(self, callback: AccountUpdateFunction) -> None:
        """
        Add a callback function to modify the account update operation.

        Args:
            callback: The function to modify the operation.

        Returns:
            None
        """
        self._callbacks.append(callback)

    def __skip_untouched_fields(
        self, previous_state: AccountUpdate2Operation, modified_state: AccountUpdate2Operation
    ) -> AccountUpdate2Operation:
        """
        Skip fields that have not been modified in the account update operation.

        Args:
            previous_state: The previous state of the account operation.
            modified_state: The modified state of the account operation.

        Returns:
            AccountUpdate2Operation: The operation with only modified fields.
        """
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
        """
        Create an account update operation from the stored state of the account.

        Args:
            account: The account object containing the current state.

        Returns:
            AccountUpdate2Operation: The operation representing the account update.
        """
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


def is_on_auths_list[T: (AccountName, PublicKey)](elem: T, auths: list[tuple[T, HiveInt]]) -> bool:
    """
    Check if element is on list of tuples.

    Args:
        elem: The element to check (either AccountName or PublicKey).
        auths: The list of tuples containing elements and their weights.

    Returns:
        bool: True if the element is found in the list, False otherwise.
    """
    return any(elem == first for first, _ in auths)


def add_account(auth: Authority, account: str, weight: int) -> Authority:
    """
    Add an account to the authority's account_auths list.

    Args:
        auth: The Authority object to modify.
        account: The account name to add.
        weight: The weight of the account authority.

    Raises:
        CLIPrettyError: If the account is already in the authority's account_auths list.

    Returns:
        Authority: The modified Authority object with the new account added.
    """
    if is_on_auths_list(AccountName(account), auth.account_auths):
        raise CLIPrettyError(f"Account {account} is current account authority")
    account_weight_tuple = (AccountName(account), HiveInt(weight))
    auth.account_auths.append(account_weight_tuple)
    return auth


def add_key(auth: Authority, key: str, weight: int) -> Authority:
    """
    Add a key to the authority's key_auths list.

    Args:
        auth: The Authority object to modify.
        key: The public key to add.
        weight: The weight of the key authority.

    Raises:
        CLIPrettyError: If the key is already in the authority's key_auths list.

    Returns:
        Authority: The modified Authority object with the new key added.
    """
    if is_on_auths_list(PublicKey(key), auth.key_auths):
        raise CLIPrettyError(f"Key {key} is current key authority")
    key_weight_tuple = (PublicKey(key), HiveInt(weight))
    auth.key_auths.append(key_weight_tuple)
    return auth


def remove_account(auth: Authority, account: str) -> Authority:
    """
    Remove an account from the authority's account_auths list.

    Args:
        auth: The Authority object to modify.
        account: The account name to remove.

    Raises:
        CLIPrettyError: If the account is not in the authority's account_auths list.

    Returns:
        Authority: The modified Authority object with the account removed.
    """
    if not is_on_auths_list(AccountName(account), auth.account_auths):
        raise CLIPrettyError(f"Account {account} is not current account authority")
    auth.account_auths = [
        account_weight_tuple for account_weight_tuple in auth.account_auths if account_weight_tuple[0] != account
    ]
    return auth


def remove_key(auth: Authority, key: str) -> Authority:
    """
    Remove a key from the authority's key_auths list.

    Args:
        auth: The Authority object to modify.
        key: The public key to remove.

    Raises:
        CLIPrettyError: If the key is not in the authority's key_auths list.

    Returns:
        Authority: The modified Authority object with the key removed.
    """
    if not is_on_auths_list(PublicKey(key), auth.key_auths):
        raise CLIPrettyError(f"Key {key} is not current key authority")
    auth.key_auths = [key_weight_tuple for key_weight_tuple in auth.key_auths if key_weight_tuple[0] != key]
    return auth


def modify_account(auth: Authority, account: str, weight: int) -> Authority:
    """
    Modify an account in the authority's account_auths list.

    Args:
        auth: The Authority object to modify.
        account: The account name to modify.
        weight: The new weight for the account authority.

    Returns:
        Authority: The modified Authority object with the account updated.
    """
    auth = remove_account(auth, account)
    return add_account(auth, account, weight)


def modify_key(auth: Authority, key: str, weight: int) -> Authority:
    """
    Modify a key in the authority's key_auths list.

    Args:
        auth: The Authority object to modify.
        key: The public key to modify.
        weight: The new weight for the key authority.

    Returns:
        Authority: The modified Authority object with the key updated.
    """
    auth = remove_key(auth, key)
    return add_key(auth, key, weight)


def set_threshold(auth: Authority, threshold: int) -> Authority:
    """
    Set the weight threshold for the authority.

    Args:
        auth: The Authority object to modify.
        threshold: The new weight threshold.

    Returns:
        Authority: The modified Authority object with the new weight threshold.
    """
    auth.weight_threshold = HiveInt(threshold)
    return auth


def set_memo_key(operation: AccountUpdate2Operation, key: str) -> AccountUpdate2Operation:
    """
    Set the memo key for the account update operation.

    Args:
        operation: The AccountUpdate2Operation to modify.
        key: The public key to set as the memo key.

    Returns:
        AccountUpdate2Operation: The modified operation with the new memo key.
    """
    operation.memo_key = PublicKey(key)
    return operation


def update_authority(
    operation: AccountUpdate2Operation, attribute: AuthorityType, callback: AuthorityUpdateFunction
) -> AccountUpdate2Operation:
    """
    Update the authority attribute of the account update operation.

    Args:
        operation: The AccountUpdate2Operation to modify.
        attribute: The authority attribute to update (owner, active, posting).
        callback: The function to apply to the authority attribute.

    Returns:
        AccountUpdate2Operation: The modified operation with the updated authority attribute.
    """
    auth_attribute = getattr(operation, attribute)
    if not auth_attribute:
        auth_attribute = Authority(weight_threshold=1, account_auths=[], key_auths=[])
        setattr(operation, attribute, auth_attribute)
    setattr(operation, attribute, callback(auth_attribute))
    return operation
