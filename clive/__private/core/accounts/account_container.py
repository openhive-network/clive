from __future__ import annotations

import contextlib
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from clive.__private.core.accounts.accounts import Account, KnownAccount, WatchedAccount
from clive.__private.core.accounts.exceptions import AccountAlreadyExistsError, AccountNotFoundError

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator


class AccountContainerBase[AccountT: Account](ABC):
    """A container-like object, that controls set of accounts."""

    def __init__(self, accounts: Iterable[AccountT] | None = None) -> None:
        """
        Initialize the account container.

        Args:
            accounts: Iterable of accounts to initialize the container with. If None, an empty set is created.

        Returns:
            None
        """
        self._accounts: set[AccountT] = set() if accounts is None else set(accounts)

    def __iter__(self) -> Iterator[AccountT]:
        """
        Iterate over the accounts in the container, sorted by name.

        Returns:
            Iterator[AccountT]: An iterator over the accounts, sorted by name.
        """
        return iter(self._sorted_accounts())

    def __len__(self) -> int:
        """
        Get the number of accounts in the container.

        Returns:
            int: The number of accounts in the container.
        """
        return len(self._accounts)

    def __bool__(self) -> bool:
        """
        Check if the container has any accounts.

        Returns:
            bool: True if there are accounts in the container, False otherwise.
        """
        return bool(self._accounts)

    @property
    def content(self) -> list[AccountT]:
        """
        Get the accounts in the container, sorted by name.

        Returns:
            list[AccountT]: A sorted list of accounts in the container.
        """
        return self._sorted_accounts()

    @abstractmethod
    def add(self, to_add: str | AccountT) -> None:
        """
        Add a new account to the container.

        Args:
            to_add: Accounts to add. If AccountT is passed, it will be added directly.
                Otherwise, a new AccountT will be created.

        Returns:
            None
        """

    def clear(self) -> None:
        """
        Clear the container, removing all accounts.

        Returns:
            None
        """
        self._accounts.clear()

    def get(self, to_get: str | Account) -> AccountT:
        """
        Get an account from the container by name or Account object.

        Args:
            to_get: The name of the account or an Account object to retrieve.

        Raises:
            AccountNotFoundError: If the account is not found in the container.

        Returns:
            AccountT: The account object if found.
        """
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
            to_remove: Accounts to remove.

        Returns:
            None
        """

        def remove_single_account(account: str | Account) -> None:
            """
            Remove a single account from the container.

            Args:
                account: The name of the account or an Account object to remove.

            Returns:
                None
            """
            with contextlib.suppress(AccountNotFoundError):
                account_obj = self.get(account)
                self._accounts.remove(account_obj)

        for acc in to_remove:
            remove_single_account(acc)

    def _sorted_accounts(self) -> list[AccountT]:
        """
        Get accounts sorted by name.

        Returns:
            list[AccountT]: A sorted list of accounts in the container.
        """
        return sorted(self._accounts, key=lambda account: account.name)

    def _add(self, *to_add: str | Account, account_type: type[AccountT]) -> None:
        """
        Add accounts to the container, ensuring no duplicates.

        Args:
            to_add: Accounts to add. If account_type is passed, it will be added directly.
                Otherwise, a new account_type will be created.
            account_type: The type of account to add (WatchedAccount or KnownAccount).

        Raises:
            AccountAlreadyExistsError: If an account with the same name already exists in the container.
        """

        def add_single_account(account: str | Account) -> None:
            """
            Add a single account to the container, ensuring it is of the correct type.

            Args:
                account: The name of the account or an Account object to add.

            Raises:
                AccountAlreadyExistsError: If an account with the same name already exists in the container.
            """
            new_account = (
                account if isinstance(account, account_type) else account_type(Account.ensure_account_name(account))
            )

            if new_account in self._accounts:
                raise AccountAlreadyExistsError(new_account.name, type(self).__name__)

            self._accounts.add(new_account)

        for acc in to_add:
            add_single_account(acc)


class WatchedAccountContainer(AccountContainerBase[WatchedAccount]):
    def add(self, *to_add: str | Account) -> None:
        """
        Add a new account to the container.

        Args:
             to_add: Accounts to add. If WatchedAccount is passed, it will be added directly.
                 Otherwise, new WatchedAccount will be created.

        Returns:
            None
        """
        self._add(*to_add, account_type=WatchedAccount)


class KnownAccountContainer(AccountContainerBase[KnownAccount]):
    def add(self, *to_add: str | Account) -> None:
        """
        Add a new account to the container.

        Args:
            to_add: Accounts to add. If KnownAccount is passed, it will be added directly.
                Otherwise, new KnownAccount will be created.

        Returns:
            None
        """
        self._add(*to_add, account_type=KnownAccount)
