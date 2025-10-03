from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.si.core.show import ShowAccounts, ShowAuthority, ShowBalances, ShowProfiles, ShowWitnesses

if TYPE_CHECKING:
    from clive.__private.si.base import ProfileBase
    from clive.__private.si.data_classes import Accounts, Authority, AuthorityInfo, Balances, Witness


class ShowInterfaceNoProfile:
    """Interface for show operations that do not require a profile."""

    def __init__(self) -> None:
        pass

    async def profiles(self) -> list[str]:
        """List all available profiles."""
        return await ShowProfiles().run()


class ShowInterface(ShowInterfaceNoProfile):
    """
    Main interface for show operations that require a profile.

    Keeps client usage unchanged (async, argument names, defaults).
    """

    def __init__(self, clive_instance: ProfileBase) -> None:
        self.clive = clive_instance

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

    async def witnesses(self, account_name: str, page_size: int = 30, page_no: int = 0) -> list[Witness]:
        """Show witnesses for an account."""
        return await ShowWitnesses(
            world=self.clive.world, account_name=account_name, page_size=page_size, page_no=page_no
        ).run()

    async def owner_authority(self, account_name: str) -> tuple[AuthorityInfo, list[Authority]]:
        """Show owner authority for an account."""
        return await ShowAuthority(
            world=self.clive.world,
            account_name=account_name,
            authority="owner",
        ).run()

    async def active_authority(self, account_name: str) -> tuple[AuthorityInfo, list[Authority]]:
        """Show active authority for an account."""
        return await ShowAuthority(
            world=self.clive.world,
            account_name=account_name,
            authority="active",
        ).run()

    async def posting_authority(self, account_name: str) -> tuple[AuthorityInfo, list[Authority]]:
        """Show posting authority for an account."""
        return await ShowAuthority(
            world=self.clive.world,
            account_name=account_name,
            authority="posting",
        ).run()
