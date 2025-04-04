from __future__ import annotations

from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand


@dataclass(kw_only=True)
class ShowAccounts(WorldBasedCommand):
    async def _run(self) -> None:
        self._show_accounts_info()

    def _show_accounts_info(self) -> None:
        profile = self.profile
        if profile.accounts.has_working_account:
            typer.echo(f"Working account: {profile.accounts.working.name}")
        else:
            typer.echo("Working account is not set.")
        typer.echo(f"Tracked accounts: {[account.name for account in profile.accounts.tracked]}")
        typer.echo(f"Known accounts: {[account.name for account in profile.accounts.known]}")
