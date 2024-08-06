from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.account_container import AccountNotFoundError, NoWorkingAccountError
from clive.__private.storage.accounts import Account, KnownAccount, TrackedAccount, WatchedAccount, WorkingAccount

if TYPE_CHECKING:
    from clive.__private.core.account_container import (
        AccountContainerBase,
        KnownAccountContainer,
        WatchedAccountContainer,
    )


class AccountManager:
    """Class for storing and managing tracked and working accounts."""

    def __init__(
        self,
        working_account: WorkingAccount | None,
        watched_accounts: WatchedAccountContainer,
        known_accounts: KnownAccountContainer,
    ) -> None:
        self._working_account = working_account
        self._watched_accounts = watched_accounts
        self._known_accounts = known_accounts

    @property
    def watched(self) -> AccountContainerBase[WatchedAccount]:
        return self._watched_accounts.copy()

    @property
    def known(self) -> AccountContainerBase[KnownAccount]:
        return self._known_accounts.copy()

    @property
    def working(self) -> WorkingAccount:
        """
        Returns the working account.

        Raises
        ------
        NoWorkingAccountError: If no working account is set.
        """
        if not self.is_working_account_set():
            raise NoWorkingAccountError
        assert self._working_account is not None
        return self._working_account

    @property
    def working_or_none(self) -> WorkingAccount | None:  # TODO: check where this is useful and use it
        if not self.is_working_account_set():
            return None
        return self._working_account

    @property
    def tracked(self) -> list[TrackedAccount]:
        """Copy of tracked accounts (watched and working together), sorted by name with working account always first."""
        accounts: set[WatchedAccount | WorkingAccount] = set(self._watched_accounts.content)
        if self.is_working_account_set():
            accounts.add(self.working)
        return sorted(
            accounts,
            key=lambda account: (not isinstance(account, WorkingAccount), account.name),
        )

    @property
    def has_known_accounts(self) -> bool:
        return bool(self._known_accounts)

    @property
    def has_tracked_accounts(self) -> bool:
        return bool(self.tracked)

    @property
    def has_watched_accounts(self) -> bool:
        return bool(self._watched_accounts)

    @property
    def has_working_account(self) -> bool:
        return self.is_working_account_set()

    @property
    def tracked_accounts_sorted(self) -> list[TrackedAccount]:
        """Working account is always first then watched accounts sorted alphabetically."""
        return sorted(
            self.tracked,
            key=lambda account: (not isinstance(account, WorkingAccount), account.name),
        )

    def _move_working_account_to_watched(self) -> None:
        name, data, alarms = self.working.name, self.working._data, self.working._alarms

        new_account_object = WatchedAccount(name, alarms)
        new_account_object._data = data

        self.unset_working_account()
        self.add_tracked_account(new_account_object)

    def _set_watched_account_as_working(self, account: Account | str) -> None:
        account = self._watched_accounts.get(account)

        self.remove_tracked_account(account)
        new_working_account = WorkingAccount(account.name, account._alarms)
        new_working_account._data = account._data

        self.set_working_account(new_working_account)

    def is_account_tracked(self, account: str | Account) -> bool:
        account_name = Account.ensure_account_name(account)
        return account_name not in [tracked_account.name for tracked_account in self.tracked]

    def is_account_working(self, account: Account | str) -> bool:
        if not self.is_working_account_set():
            return False

        account_name = Account.ensure_account_name(account)
        return self.working.name == account_name

    def is_working_account_set(self) -> bool:
        return self._working_account is not None

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

    def unset_working_account(self) -> None:
        self._working_account = None

    def set_working_account(self, value: str | WorkingAccount) -> None:
        if isinstance(value, str):
            value = WorkingAccount(value)
        self._working_account = value

    def switch_working_account(self, new_working_account: str | Account | None = None) -> None:
        """
        Switch the working account to the one of watched accounts and move the old one to the watched accounts.

        Working account can be deleted and moved to watched accounts if `new_working_account` is None.
        """

        def is_given_account_already_working() -> bool:
            return new_working_account is not None and self.is_account_working(new_working_account)

        if is_given_account_already_working():
            return

        if self.is_working_account_set():
            # we allow for switching from no working account to watched account
            self._move_working_account_to_watched()

        if new_working_account is not None:
            # we allow for only moving the current working account to watched accounts
            self._set_watched_account_as_working(new_working_account)

    def add_tracked_account(self, to_add: str | WatchedAccount) -> None:
        self._watched_accounts.add(to_add)

    def remove_tracked_account(self, to_remove: str | Account) -> None:
        account_name = Account.ensure_account_name(to_remove)
        if self.is_working_account_set() and account_name == self.working.name:
            self.unset_working_account()
        else:
            self.watched.remove(to_remove)

    def get_tracked_account(self, value: str | TrackedAccount) -> TrackedAccount:
        searched_account_name = Account.ensure_account_name(value)
        for account in self.tracked:
            if account.name == searched_account_name:
                return account

        raise AccountNotFoundError(searched_account_name)
