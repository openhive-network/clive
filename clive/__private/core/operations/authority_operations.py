"""Shared authority modification operations for both SI and CLI."""

from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.models.schemas import AccountName, AccountUpdate2Operation, Authority, HiveInt, PublicKey

if TYPE_CHECKING:
    from collections.abc import Callable

    from clive.__private.core.types import AuthorityLevelRegular
    from clive.__private.models.schemas import Account


class AuthorityAlreadyExistsError(Exception):
    """Raised when trying to add a key or account that already exists in authority."""


class AuthorityNotFoundError(Exception):
    """Raised when trying to remove or modify a key or account that doesn't exist in authority."""


def is_on_auths_list[T: (AccountName, PublicKey)](authority_entry: T, authorities: list[tuple[T, HiveInt]]) -> bool:
    """
    Check if the authority entry is on the hive-like authorities list.

    Args:
        authority_entry: Authority entry.
        authorities: Hive-like format of authority entries and their weights.

    Returns:
        True if the authority entry is found, False otherwise.
    """
    return any(authority_entry == entry for entry, _ in authorities)


def set_threshold(auth: Authority, threshold: int) -> Authority:
    """Set the weight threshold for an authority."""
    auth.weight_threshold = HiveInt(threshold)
    return auth


def add_key(auth: Authority, key: str, weight: int) -> Authority:
    """Add a key to the authority."""
    # Check if key already exists
    if is_on_auths_list(PublicKey(key), auth.key_auths):
        raise AuthorityAlreadyExistsError(f"Key {key} is already in authority")

    key_weight_tuple = (PublicKey(key), HiveInt(weight))
    auth.key_auths.append(key_weight_tuple)
    return auth


def add_account(auth: Authority, account: str, weight: int) -> Authority:
    """Add an account to the authority."""
    # Check if account already exists
    if is_on_auths_list(AccountName(account), auth.account_auths):
        raise AuthorityAlreadyExistsError(f"Account {account} is already in authority")

    account_weight_tuple = (AccountName(account), HiveInt(weight))
    auth.account_auths.append(account_weight_tuple)
    return auth


def remove_key(auth: Authority, key: str) -> Authority:
    """Remove a key from the authority."""
    # Check if key exists
    if not is_on_auths_list(PublicKey(key), auth.key_auths):
        raise AuthorityNotFoundError(f"Key {key} is not in authority")

    auth.key_auths = [kw for kw in auth.key_auths if kw[0] != key]
    return auth


def remove_account(auth: Authority, account: str) -> Authority:
    """Remove an account from the authority."""
    # Check if account exists
    if not is_on_auths_list(AccountName(account), auth.account_auths):
        raise AuthorityNotFoundError(f"Account {account} is not in authority")

    auth.account_auths = [aw for aw in auth.account_auths if aw[0] != account]
    return auth


def modify_key(auth: Authority, key: str, weight: int) -> Authority:
    """Modify the weight of a key in the authority."""
    auth = remove_key(auth, key)
    return add_key(auth, key, weight)


def modify_account(auth: Authority, account: str, weight: int) -> Authority:
    """Modify the weight of an account in the authority."""
    auth = remove_account(auth, account)
    return add_account(auth, account, weight)


def build_account_update_operation(
    account: Account,
    authority_type: AuthorityLevelRegular,
    callbacks: list[Callable[[Authority], Authority]],
) -> AccountUpdate2Operation:
    """
    Build an account_update2_operation by applying callbacks to modify an authority.

    Args:
        account: Current account state from blockchain
        authority_type: Which authority to modify ('owner', 'active', 'posting')
        callbacks: List of functions to apply to the authority

    Returns:
        AccountUpdate2Operation with only the modified authority field set
    """
    # Create operation from current account state
    operation = AccountUpdate2Operation(
        account=account.name,
        owner=account.owner,
        active=account.active,
        posting=account.posting,
        memo_key=account.memo_key,
        json_metadata="",
        posting_json_metadata="",
        extensions=[],
    )

    # Get the authority we're modifying
    authority = getattr(operation, authority_type)

    # Apply all callbacks to modify the authority
    for callback in callbacks:
        authority = callback(authority)

    # Set the modified authority back
    setattr(operation, authority_type, authority)

    # Only include the modified authority field in the operation
    # Set all other authority fields to None
    for attr in ["owner", "active", "posting"]:
        if attr != authority_type:
            setattr(operation, attr, None)

    # Set memo_key to None (we don't modify it in authority updates)
    operation.memo_key = None

    return operation
