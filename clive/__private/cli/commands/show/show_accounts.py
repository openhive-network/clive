from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.print_cli import print_cli
from clive.__private.si.core.show import ShowAccounts as ShowAccountsSi


@dataclass(kw_only=True)
class ShowAccounts(WorldBasedCommand):
    async def _run(self) -> None:
        await self._show_accounts_info()

    async def _show_accounts_info(self) -> None:
        accounts = await ShowAccountsSi(world=self.world).run()
        if accounts.working_account is not None:
            print_cli(f"Working account: {accounts.working_account}")
        else:
            print_cli("Working account is not set.")
        print_cli(f"Tracked accounts: {accounts.tracked_accounts}")
        print_cli(f"Known accounts: {accounts.known_accounts}")
