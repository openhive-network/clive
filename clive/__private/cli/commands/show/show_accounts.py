from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.profile_based_command import ProfileBasedCommand


@dataclass(kw_only=True)
class ShowAccounts(ProfileBasedCommand):
    async def _run(self) -> None:
        self._show_accounts_info()

    def _show_accounts_info(self) -> None:
        profile = self.profile_data
        if profile.accounts.has_working_account:
            typer.echo(f"Working account: {profile.accounts.working.name}")
        else:
            typer.echo("Working account is not set.")
        typer.echo(f"Watched accounts: {[account.name for account in profile.accounts.watched]}")
        typer.echo(f"Known accounts: {[account.name for account in profile.accounts.known]}")
