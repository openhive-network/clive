import errno
from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.profile_based_command import ProfileBasedCommand
from clive.__private.cli_error import CLIError
from clive.__private.storage.accounts import WorkingAccount


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
class AccountsWorkingSet(ProfileBasedCommand):
    account_name: str

    async def run(self) -> None:
        if self.profile_data.is_working_account_set():
            raise CLIError("Working account is already set.", errno.EEXIST)

        self.profile_data.working_account = WorkingAccount(name=self.account_name)
