from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.print_cli import print_cli


@dataclass(kw_only=True)
class ShowAccounts(WorldBasedCommand):
    async def _run(self) -> None:
        self._show_accounts_info()

    def _show_accounts_info(self) -> None:
        profile = self.profile
        if profile.accounts.has_working_account:
            print_cli(f"Working account: {profile.accounts.working.name}")
        else:
            print_cli("Working account is not set.")
        print_cli(f"Tracked accounts: {[account.name for account in profile.accounts.tracked]}")
        print_cli(f"Known accounts: {[account.name for account in profile.accounts.known]}")
