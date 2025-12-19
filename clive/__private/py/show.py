from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.py.foundation.show import ShowAccounts, ShowAuthority, ShowBalances, ShowProfiles, ShowWitnesses

if TYPE_CHECKING:
    from clive.__private.core.types import AuthorityLevelRegular
    from clive.__private.py.base import UnlockedClivePy
    from clive.__private.py.data_classes import Accounts, AuthorityInfo, Balances, WitnessesResult


class ShowInterfaceNoProfile:
    """Interface for show operations that do not require a profile."""

    async def profiles(self) -> list[str]:
        """List all available profiles."""
        return await ShowProfiles().run()


class ShowInterface:
    """
    Main interface for show operations that require a profile.

    Uses composition instead of inheritance to avoid LSP violation.
    Keeps client usage unchanged (async, argument names, defaults).
    """

    def __init__(self, clive_instance: UnlockedClivePy) -> None:
        self.clive = clive_instance
        self._no_profile = ShowInterfaceNoProfile()

    async def profiles(self) -> list[str]:
        """
        List all available profiles.

        Delegates to ShowInterfaceNoProfile implementation.
        """
        return await self._no_profile.profiles()

    async def balances(self, account_name: str) -> Balances:
        """Show balances for an account."""
        return await ShowBalances(
            world=self.clive.world,
            account_name=account_name,
        ).run()

    async def accounts(self) -> Accounts:
        """Show accounts information."""
        return await ShowAccounts(
            world=self.clive.world,
        ).run()

    async def witnesses(self, account_name: str, page_size: int = 30, page_no: int = 0) -> WitnessesResult:
        """
        Show witnesses for an account with pagination metadata.

        Note:
            If page_no exceeds available pages, returns empty witnesses list
            without raising an error.
        """
        return await ShowWitnesses(
            world=self.clive.world, account_name=account_name, page_size=page_size, page_no=page_no
        ).run()

    async def _get_authority(self, account_name: str, authority: AuthorityLevelRegular) -> AuthorityInfo:
        """Helper method to get authority information for a specific authority type."""
        return await ShowAuthority(
            world=self.clive.world,
            account_name=account_name,
            authority=authority,
        ).run()

    async def owner_authority(self, account_name: str) -> AuthorityInfo:
        """Show owner authority for an account."""
        return await self._get_authority(account_name, "owner")

    async def active_authority(self, account_name: str) -> AuthorityInfo:
        """Show active authority for an account."""
        return await self._get_authority(account_name, "active")

    async def posting_authority(self, account_name: str) -> AuthorityInfo:
        """Show posting authority for an account."""
        return await self._get_authority(account_name, "posting")
