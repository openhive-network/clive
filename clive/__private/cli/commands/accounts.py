from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.profile_based_command import ProfileBasedCommand


@dataclass(kw_only=True)
class AccountsList(ProfileBasedCommand):
    async def run(self) -> None:
        profile = self._load_profile()

        if profile.is_working_account_set():
            typer.echo(f"Working account: {profile.working_account.name}")
        else:
            typer.echo("Working account is not set.")
        typer.echo(f"Watched accounts: {[account.name for account in profile.watched_accounts]}")
        typer.echo(f"Known accounts: {[account.name for account in profile.known_accounts]}")
