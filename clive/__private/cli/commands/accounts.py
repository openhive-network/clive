from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.profile_based_command import ProfileBasedCommand
from clive.__private.cli.exceptions import CLIWorkingAccountIsNotSetError


@dataclass(kw_only=True)
class AccountsList(ProfileBasedCommand):
    async def run(self) -> None:
        self._show_accounts_info()

    def _show_accounts_info(self) -> None:
        profile = self.profile_data
        if profile.is_working_account_set():
            typer.echo(f"Working account: {profile.working_account.name}")
        else:
            typer.echo("Working account is not set.")
        typer.echo(f"Watched accounts: {[account.name for account in profile.watched_accounts]}")
        typer.echo(f"Known accounts: {[account.name for account in profile.known_accounts]}")


@dataclass(kw_only=True)
class AccountsWorkingShow(ProfileBasedCommand):
    async def run(self) -> None:
        if not self.profile_data.is_working_account_set():
            raise CLIWorkingAccountIsNotSetError(self.profile_data)

        typer.echo(self.profile_data.working_account.name)


@dataclass(kw_only=True)
class AccountsWatchedList(ProfileBasedCommand):
    async def run(self) -> None:
        account_names = [account.name for account in self.profile_data.watched_accounts]
        typer.echo(str(account_names))
