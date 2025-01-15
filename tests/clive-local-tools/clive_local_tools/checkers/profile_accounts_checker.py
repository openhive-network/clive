from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, Literal

from clive.__private.core.profile import Profile

if TYPE_CHECKING:
    from clive.__private.core.encryption import EncryptionService


class IsNotSet:
    """A class to represent a value that is not set."""


class ProfileAccountsChecker:
    def __init__(self, profile_name: str, encryption_service: EncryptionService) -> None:
        self._profile_name = profile_name
        self._encryption_service = encryption_service

    @property
    async def profile(self) -> Profile:
        return await Profile.load(self._profile_name, self._encryption_service)

    async def assert_working_account(self, working_account: str | IsNotSet | None = None) -> None:
        """
        Check working account of profile.

        Args:
        working_account: The name of the working account to check. For:
        * IsNotSet - check if the working account is not set,
        * None - skip the check.
        """
        if working_account is not None:
            profile = await self.profile
            is_working_account_set = profile.accounts.has_working_account

            if isinstance(working_account, IsNotSet):
                assert not is_working_account_set, "Working account is set while should not be."
            else:
                assert is_working_account_set, f"Working account is not set while should be {working_account}."
                assert working_account == profile.accounts.working.name, (
                    f"Working account is set to '{profile.accounts.working.name}' ",
                    f"while should be '{working_account}'.",
                )

    async def assert_in_tracked_accounts(self, account_names: Iterable[str] | None = None) -> None:
        profile = await self.profile
        tracked_account_names = [account.name for account in profile.accounts.tracked]
        self._assert_account_presence(tracked_account_names, account_names, "Tracked")

    async def assert_not_in_tracked_accounts(self, account_names: Iterable[str] | None = None) -> None:
        profile = await self.profile
        tracked_account_names = [account.name for account in profile.accounts.tracked]
        self._assert_account_absence(tracked_account_names, account_names, "Tracked")

    async def assert_in_known_accounts(self, account_names: Iterable[str] | None = None) -> None:
        profile = await self.profile
        known_account_names = [account.name for account in profile.accounts.known]
        self._assert_account_presence(known_account_names, account_names, "Known")

    async def assert_not_in_known_accounts(self, account_names: Iterable[str] | None = None) -> None:
        profile = await self.profile
        known_account_names = [account.name for account in profile.accounts.known]
        self._assert_account_absence(known_account_names, account_names, "Known")

    def _assert_account_presence(
        self,
        actual_accounts: Iterable[str],
        expected_accounts: Iterable[str] | None,
        account_type: Literal["Tracked", "Known"],
    ) -> None:
        """Assert presence of accounts in a list of account."""
        if not expected_accounts:
            return

        expected_accounts_ = list(expected_accounts)
        actual_accounts_ = list(actual_accounts)
        for account in expected_accounts_:
            assert account in actual_accounts_, (
                f"{account_type} account '{account}' is missing while should be present.\n"
                f"Expected: {expected_accounts_} to be present in: {actual_accounts_}"
            )

    def _assert_account_absence(
        self,
        actual_accounts: Iterable[str],
        absence_accounts: Iterable[str] | None,
        account_type: Literal["Tracked", "Known"],
    ) -> None:
        """Assert absence of accounts in a list of account."""
        if not absence_accounts:
            return

        absence_accounts_ = list(absence_accounts)
        actual_accounts_ = list(actual_accounts)
        for account in absence_accounts_:
            assert account not in actual_accounts_, (
                f"{account_type} account '{account}' is present while should not be.\n"
                f"Expected: {absence_accounts_} not to be present in: {actual_accounts_}"
            )
