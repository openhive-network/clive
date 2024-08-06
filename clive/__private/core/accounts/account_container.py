from __future__ import annotations

import contextlib
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from clive.__private.core.accounts.exceptions import AccountNotFoundError
from clive.__private.storage.accounts import Account, KnownAccount, WatchedAccount
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator


AccountT = TypeVar("AccountT", KnownAccount, WatchedAccount)


class AccountContainerError(CliveError):
    """Base class for errors related with account containers."""


class AccountAlreadyExistsError(AccountContainerError):
    """Raised when account already exists in the container."""

    def __init__(self, account_name: str, container: AccountContainerBase[Any]) -> None:
        super().__init__(f"Account {account_name} already exists in {type(container).__name__}.")
        self.account_name = account_name
        self.container = container


class AccountContainerBase(ABC, Generic[AccountT]):
    """A container-like object, that controls set of accounts."""

    def __init__(self, accounts: Iterable[AccountT] | None = None) -> None:
        self._accounts: set[AccountT] = set() if accounts is None else set(accounts)

    def __iter__(self) -> Iterator[AccountT]:
        return iter(self._sorted_accounts())

    def __len__(self) -> int:
        return len(self._accounts)

    def __bool__(self) -> bool:
        return bool(self._accounts)

    @property
    def content(self) -> list[AccountT]:
        return self._sorted_accounts()

    @abstractmethod
    def add(self, to_add: str | AccountT) -> None:
        pass

    def clear(self) -> None:
        self._accounts.clear()

    def get(self, to_get: str | Account) -> AccountT:
        searched_account_name = Account.ensure_account_name(to_get)
        for account in self._accounts:
            if account.name == searched_account_name:
                return account

        raise AccountNotFoundError(searched_account_name)

    def remove(self, *to_remove: str | Account) -> None:
        """
        Remove accounts from the container.

        Won't raise an error if the account is not found.

        Args:
        ----
            to_remove: Accounts to remove.
        """

        def remove_single_account(account: str | Account) -> None:
            with contextlib.suppress(AccountNotFoundError):
                account_obj = self.get(account)
                self._accounts.remove(account_obj)

        for acc in to_remove:
            remove_single_account(acc)

    def _sorted_accounts(self) -> list[AccountT]:
        """Get accounts sorted by name."""
        return sorted(self._accounts, key=lambda account: account.name)

    def _add(self, *to_add: str | Account, account_type: type[AccountT]) -> None:
        def add_single_account(account: str | Account) -> None:
            new_account = (
                account if isinstance(account, account_type) else account_type(Account.ensure_account_name(account))
            )

            if new_account in self._accounts:
                raise AccountAlreadyExistsError(new_account.name, self)

            self._accounts.add(new_account)

        for acc in to_add:
            add_single_account(acc)


class WatchedAccountContainer(AccountContainerBase[WatchedAccount]):
    def add(self, *to_add: str | Account) -> None:
        """
        Add a new account to the container.

        Args:
        ----
             to_add: Accounts to add. If WatchedAccount is passed, it will be added directly.
                 Otherwise, new WatchedAccount will be created.
        """
        self._add(*to_add, account_type=WatchedAccount)


class KnownAccountContainer(AccountContainerBase[KnownAccount]):
    def add(self, *to_add: str | Account) -> None:
        """
        Add a new account to the container.

        Args:
        ----
            to_add: Accounts to add. If KnownAccount is passed, it will be added directly.
                Otherwise, new KnownAccount will be created.
        """
        self._add(*to_add, account_type=KnownAccount)
