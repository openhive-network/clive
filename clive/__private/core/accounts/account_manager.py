from __future__ import annotations

from typing import Iterable

from clive.__private.core.accounts.account_container import (
    KnownAccountContainer,
    WatchedAccountContainer,
)
from clive.__private.core.accounts.accounts import Account, TrackedAccount, WatchedAccount, WorkingAccount
from clive.__private.core.accounts.exceptions import (
    AccountAlreadyExistsError,
    AccountNotFoundError,
    NoWorkingAccountError,
)


class AccountManager:
    """Class for storing and managing accounts."""

    def __init__(
        self,
        working_account: str | Account | None = None,
        watched_accounts: Iterable[str | Account] | None = None,
        known_accounts: Iterable[str | Account] | None = None,
    ) -> None:
        self._working_account: WorkingAccount | None = None
        self._watched_accounts = WatchedAccountContainer()
        self._known_accounts = KnownAccountContainer()

        if working_account is not None:
            self.set_working_account(working_account)

        if watched_accounts:
            self.watched.add(*watched_accounts)

        if known_accounts:
            self.known.add(*known_accounts)

    @property
    def working(self) -> WorkingAccount:
        """
        Returns the working account.

        Raises:  # noqa: D406
        ------
            NoWorkingAccountError: If no working account is set.
        """
        if not self.has_working_account:
            raise NoWorkingAccountError
        assert self._working_account is not None, "Working account should be ensured by earlier check."
        return self._working_account

    @property
    def working_or_none(self) -> WorkingAccount | None:
        """Same as `working`, but returns None if no working account is set."""
        if not self.has_working_account:
            return None
        return self._working_account

    @property
    def watched(self) -> WatchedAccountContainer:
        return self._watched_accounts

    @property
    def known(self) -> KnownAccountContainer:
        return self._known_accounts

    @property
    def tracked(self) -> list[TrackedAccount]:
        """Get a new list of tracked accounts (watched and working) sorted by name with working account always first."""
        accounts: set[WatchedAccount | WorkingAccount] = set(self._watched_accounts.content)
        if self.has_working_account:
            accounts.add(self.working)
        return sorted(
            accounts,
            key=lambda account: (not isinstance(account, WorkingAccount), account.name),
        )

    @property
    def has_working_account(self) -> bool:
        return self._working_account is not None

    @property
    def has_watched_accounts(self) -> bool:
        return bool(self._watched_accounts)

    @property
    def has_known_accounts(self) -> bool:
        return bool(self._known_accounts)

    @property
    def has_tracked_accounts(self) -> bool:
        return bool(self.tracked)

    @property
    def is_tracked_accounts_alarms_data_available(self) -> bool:
        tracked_accounts = self.tracked
        if not tracked_accounts:
            return False

        return all(account.is_alarms_data_available for account in tracked_accounts)

    @property
    def is_tracked_accounts_node_data_available(self) -> bool:
        tracked_accounts = self.tracked
        if not tracked_accounts:
            return False

        return all(account.is_node_data_available for account in tracked_accounts)

    def is_account_working(self, account: str | Account) -> bool:
        if not self.has_working_account:
            return False

        account_name = Account.ensure_account_name(account)
        return self.working.name == account_name

    def is_account_watched(self, account: str | Account) -> bool:
        account_name = Account.ensure_account_name(account)
        return account_name in [watched_account.name for watched_account in self.watched]

    def is_account_known(self, account: str | Account) -> bool:
        account_name = Account.ensure_account_name(account)
        return account_name in [known_account.name for known_account in self.known]

    def is_account_tracked(self, account: str | Account) -> bool:
        account_name = Account.ensure_account_name(account)
        return account_name in [tracked_account.name for tracked_account in self.tracked]

    def set_working_account(self, value: str | Account) -> None:
        """
        Set the working account.

        Args:
        ----
            value: The account to set as working account.  If WorkingAccount is passed, it will be set directly.
                Otherwise, new WorkingAccount will be created.
        """
        self._working_account = (
            value if isinstance(value, WorkingAccount) else WorkingAccount(Account.ensure_account_name(value))
        )

    def unset_working_account(self) -> None:
        self._working_account = None

    def switch_working_account(self, new_working_account: str | Account | None = None) -> None:
        """
        Switch the working account to one of the watched accounts and move the old one to the watched accounts.

        Working account can be deleted and moved to watched accounts if `new_working_account` is None.
        Method will look for corresponding watched account by name if `new_working_account` is filled.

        Args:
        ----
            new_working_account: The new working account to switch to.
                -  will set the given watched account as working and move the current working to watched accounts.
                -  will only move the current working account to watched accounts if None.

        Raises:
        ------
            AccountNotFoundError: If given account wasn't found in watched accounts.
        """

        def is_given_account_already_working() -> bool:
            return new_working_account is not None and self.is_account_working(new_working_account)

        if is_given_account_already_working():
            return

        if self.has_working_account:
            # we allow for switching from no working account to watched account
            self._move_working_account_to_watched()

        if new_working_account is not None:
            # we allow for only moving the current working account to watched accounts
            self._set_watched_account_as_working(new_working_account)

    def add_tracked_account(self, *to_add: str | Account) -> None:
        """
        Add accounts to the tracked (working + watched) accounts.

        When there's no working account, the first account from the list will be set as working account.

        Args:
        ----
            to_add: Accounts to add.

        Raises:
        ------
            AccountAlreadyExistsError: If any of the accounts already exists in tracked accounts
                (either as working or watched).
        """
        if not to_add:
            return

        if not self.has_working_account:
            first_account_to_add = to_add[0]
            self.set_working_account(first_account_to_add)
            to_add = to_add[1:]

        # raise AccountAlreadyExistsError if any of the accounts is already a working account
        for account in to_add:
            if self.is_account_working(account):
                raise AccountAlreadyExistsError(Account.ensure_account_name(account), "WorkingAccount")

        self.watched.add(*to_add)

    def remove_tracked_account(self, *to_remove: str | Account) -> None:
        """
        Remove accounts from tracked accounts.

        Won't raise an error if the account is not found.

        Args:
        ----
            to_remove: Accounts to remove.
        """
        should_unset_working_account = any(self.is_account_working(account) for account in to_remove)
        if should_unset_working_account:
            self.unset_working_account()
        self.watched.remove(*to_remove)

    def get_tracked_account(self, value: str | Account) -> TrackedAccount:
        """
        Get tracked account by name.

        Raises:  # noqa: D406
        ------
            AccountNotFoundError: If given account wasn't found.
        """
        searched_account_name = Account.ensure_account_name(value)
        for account in self.tracked:
            if account.name == searched_account_name:
                return account

        raise AccountNotFoundError(searched_account_name)

    def _move_working_account_to_watched(self) -> None:
        """
        Move the working account to watched accounts.

        Working account will be unset and moved to watched accounts.
        """
        self.watched.add(WatchedAccount.create_from_working(self.working))
        self.unset_working_account()

    def _set_watched_account_as_working(self, watched_account: str | Account) -> None:
        """
        Set the given watched account as working account.

        Will look for the account by name in watched accounts and set it as working account, removing the watched one.

        Raises: # noqa: D406
        ------
             AccountNotFoundError: If given account wasn't found in watched accounts.
        """
        watched_account = self._watched_accounts.get(watched_account)
        self.watched.remove(watched_account)
        self.set_working_account(WorkingAccount.create_from_watched(watched_account))
