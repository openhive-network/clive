from __future__ import annotations

from abc import ABC, abstractmethod
from copy import copy
from typing import TYPE_CHECKING, Generic, TypeVar

from clive.__private.storage.accounts import Account, KnownAccount, WatchedAccount
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator


class AccountMissingError(CliveError):
    """An error related with missing account."""


class NoWorkingAccountError(AccountMissingError):
    """No working account is available."""


class AccountNotFoundError(AccountMissingError):
    """Raised when an account is not found in `get_tracked_account` method."""

    def __init__(self, account_name: str) -> None:
        super().__init__(f"Account {account_name} not found in tracked accounts (working + watched accounts)")
        self.account_name = account_name


AccountT = TypeVar("AccountT", KnownAccount, WatchedAccount)


class AccountContainerBase(ABC, Generic[AccountT]):
    """A container-like object, that controls set of accounts."""

    def __init__(self, accounts: Iterable[AccountT] | None) -> None:
        self._accounts: set[AccountT] = set() if accounts is None else set(accounts)

    def __iter__(self) -> Iterator[AccountT]:
        return iter(self._accounts.copy())

    def __len__(self) -> int:
        return len(self._accounts)

    def __bool__(self) -> bool:
        return bool(self._accounts)

    @abstractmethod
    def add(self, to_add: AccountT | str) -> None:
        pass

    def clear(self) -> None:
        self._accounts.clear()

    @property
    def content(self) -> set[AccountT]:
        return self._accounts.copy()

    def copy(self) -> AccountContainerBase[AccountT]:
        return copy(self)

    def get(self, to_get: Account | str) -> AccountT:
        searched_account_name = Account.ensure_account_name(to_get)
        for account in self._accounts:
            if account.name == searched_account_name:
                return account

        raise AccountNotFoundError(searched_account_name)

    def remove(self, to_remove: Account | str) -> None:
        account_name = Account.ensure_account_name(to_remove)
        account = next((account for account in self._accounts if account.name == account_name), None)
        if account is not None:
            self._accounts.remove(account)


class WatchedAccountContainer(AccountContainerBase[WatchedAccount]):
    def add(self, to_add: WatchedAccount | str) -> None:
        self._accounts.add(to_add) if isinstance(to_add, WatchedAccount) else self._accounts.add(WatchedAccount(to_add))


class KnownAccountContainer(AccountContainerBase[KnownAccount]):
    def add(self, to_add: KnownAccount | str) -> None:
        self._accounts.add(to_add) if isinstance(to_add, KnownAccount) else self._accounts.add(KnownAccount(to_add))
