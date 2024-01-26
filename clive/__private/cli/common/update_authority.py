from __future__ import annotations

import typing
from typing import TYPE_CHECKING, Literal

from schemas.fields.basic import AccountName, PublicKey
from schemas.fields.compound import Authority
from schemas.fields.hive_int import HiveInt

if TYPE_CHECKING:
    from collections.abc import Callable

    from schemas.operations import AccountUpdate2Operation

    AccountUpdateFunction = Callable[[AccountUpdate2Operation], AccountUpdate2Operation]
    AuthorityUpdateFunction = Callable[[Authority], Authority]
    ApplyCallbackToAuthority = Callable[[AccountUpdate2Operation, AuthorityUpdateFunction], AccountUpdate2Operation]

    AccountOrKey = typing.TypeVar("AccountOrKey", AccountName, PublicKey)


AuthorityType = Literal["owner", "active", "posting"]


def is_on_auths_list(elem: AccountOrKey, auths: list[tuple[AccountOrKey, HiveInt]]) -> bool:
    """Check if element is on list of tuples."""
    for first, _ in auths:
        if elem == first:
            break
    else:
        return False
    return True


def add_account(auth: Authority, account: str, weight: int) -> Authority:
    assert not is_on_auths_list(
        AccountName(account), auth.account_auths
    ), f"Account {account} is current account authority"
    account_weight_tuple = (AccountName(account), HiveInt(weight))
    auth.account_auths.append(account_weight_tuple)
    return auth


def add_key(auth: Authority, key: str, weight: int) -> Authority:
    assert not is_on_auths_list(PublicKey(key), auth.key_auths), f"Key {key} is current key authority"
    key_weight_tuple = (PublicKey(key), HiveInt(weight))
    auth.key_auths.append(key_weight_tuple)
    return auth


def remove_account(auth: Authority, account: str) -> Authority:
    assert is_on_auths_list(
        AccountName(account), auth.account_auths
    ), f"Account {account} is not current account authority"
    auth.account_auths = [
        account_weight_tuple for account_weight_tuple in auth.account_auths if account_weight_tuple[0] != account
    ]
    return auth


def remove_key(auth: Authority, key: str) -> Authority:
    assert is_on_auths_list(PublicKey(key), auth.key_auths), f"Key {key} is not current key authority"
    auth.key_auths = [key_weight_tuple for key_weight_tuple in auth.key_auths if key_weight_tuple[0] != key]
    return auth


def modify_account(auth: Authority, account: str, weight: int) -> Authority:
    auth = remove_account(auth, account)
    return add_account(auth, account, weight)


def modify_key(auth: Authority, key: str, weight: int) -> Authority:
    auth = remove_key(auth, key)
    return add_key(auth, key, weight)


def set_threshold(auth: Authority, threshold: int) -> Authority:
    auth.weight_threshold = HiveInt(threshold)
    return auth


def update_owner(operation: AccountUpdate2Operation, callback: AuthorityUpdateFunction) -> AccountUpdate2Operation:
    if not operation.owner:
        operation.owner = Authority(weight_threshold=1, account_auths=[], key_auths=[])
    operation.owner = callback(operation.owner)
    return operation


def update_active(operation: AccountUpdate2Operation, callback: AuthorityUpdateFunction) -> AccountUpdate2Operation:
    if not operation.active:
        operation.active = Authority(weight_threshold=1, account_auths=[], key_auths=[])
    operation.active = callback(operation.active)
    return operation


def update_posting(operation: AccountUpdate2Operation, callback: AuthorityUpdateFunction) -> AccountUpdate2Operation:
    if not operation.posting:
        operation.posting = Authority(weight_threshold=1, account_auths=[], key_auths=[])
    operation.posting = callback(operation.posting)
    return operation


def set_memo_key(operation: AccountUpdate2Operation, key: str) -> AccountUpdate2Operation:
    operation.memo_key = PublicKey(key)
    return operation
