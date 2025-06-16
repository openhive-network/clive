from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Final, Literal, Self

from clive.__private.core.beekeeper_manager import BeekeeperManager
from clive.__private.core.commands.get_unlocked_encryption_wallet import GetUnlockedEncryptionWallet
from clive.__private.core.commands.get_unlocked_user_wallet import GetUnlockedUserWallet
from clive.__private.core.commands.load_profile import LoadProfile
from clive.__private.core.commands.unlock import Unlock
from clive.__private.core.profile import Profile
from clive.__private.core.wallet_container import WalletContainer

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Iterable


class IsNotSet:
    """A class to represent a value that is not set."""


class ProfileChecker:
    _INIT_KEY: Final[object] = object()
    """Used to prevent direct initialization of the class. Instead factory methods should be used."""

    def __init__(self, init_key: object, profile_name: str, wallets: WalletContainer) -> None:
        self._assert_no_direct_initialization(init_key)

        self._profile_name = profile_name
        self._wallets = wallets
        self._beekeeper_manager: BeekeeperManager | None = None

    @classmethod
    def from_wallets(cls, profile_name: str, wallets: WalletContainer) -> Self:
        return cls(cls._INIT_KEY, profile_name, wallets)

    @classmethod
    @asynccontextmanager
    async def from_password(cls, profile_name: str, password: str) -> AsyncGenerator[Self]:
        beekeeper_manager = BeekeeperManager()
        await beekeeper_manager.setup()
        await (
            Unlock(
                password=password,
                session=beekeeper_manager.session,
                profile_name=profile_name,
            )
        ).execute()
        unlocked_user_wallet = await (GetUnlockedUserWallet(session=beekeeper_manager.session)).execute_with_result()
        unlocked_encryption_wallet = await (
            GetUnlockedEncryptionWallet(session=beekeeper_manager.session)
        ).execute_with_result()
        await beekeeper_manager.set_wallets(WalletContainer(unlocked_user_wallet, unlocked_encryption_wallet))
        checker = cls(cls._INIT_KEY, profile_name, beekeeper_manager._content)
        checker._beekeeper_manager = beekeeper_manager
        yield checker
        beekeeper_manager.teardown()

    @property
    async def profile(self) -> Profile:
        return await LoadProfile(
            profile_name=self._profile_name,
            unlocked_wallet=self._wallets.user_wallet,
            unlocked_encryption_wallet=self._wallets.encryption_wallet,
        ).execute_with_result()

    @classmethod
    def assert_profile_is_stored(cls, profile_name: str, *, should_be_stored: bool = True, context: str = "") -> None:
        is_stored = Profile.is_profile_stored(profile_name)
        message = (
            "Profile is not stored while should be." if should_be_stored else "Profile is stored while should not be."
        )
        if context:
            message += f" Context: {context}"
        assert is_stored == should_be_stored, message

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

    def _assert_no_direct_initialization(self, init_key: object) -> None:
        message = (
            f"Please use factory methods {self.from_wallets} to or {self.from_password} "
            "as context manager to create instance."
        )
        assert init_key is self._INIT_KEY, message
