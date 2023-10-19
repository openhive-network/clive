from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.profile_based_command import ProfileBasedCommand
from clive.__private.cli.exceptions import CLIWorkingAccountIsAlreadySetError, CLIWorkingAccountIsNotSetError
from clive.__private.storage.accounts import Account


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
            raise CLIWorkingAccountIsAlreadySetError(self.profile_data)

        self.profile_data.set_working_account(self.account_name)


@dataclass(kw_only=True)
class AccountsWorkingUnset(ProfileBasedCommand):
    async def run(self) -> None:
        if not self.profile_data.is_working_account_set():
            raise CLIWorkingAccountIsNotSetError(self.profile_data)

        self.profile_data.unset_working_account()


@dataclass(kw_only=True)
class AccountsWorkingShow(ProfileBasedCommand):
    async def run(self) -> None:
        if not self.profile_data.is_working_account_set():
            raise CLIWorkingAccountIsNotSetError(self.profile_data)

        typer.echo(self.profile_data.working_account.name)


@dataclass(kw_only=True)
class AccountsWatchedAdd(ProfileBasedCommand):
    account_name: str

    async def run(self) -> None:
        self.profile_data.watched_accounts.add(Account(self.account_name))


@dataclass(kw_only=True)
class AccountsWatchedRemove(ProfileBasedCommand):
    account_name: str

    async def run(self) -> None:
        account = next(
            (account for account in self.profile_data.watched_accounts if account.name == self.account_name), None
        )
        if account is not None:
            self.profile_data.watched_accounts.discard(account)


@dataclass(kw_only=True)
class AccountsWatchedList(ProfileBasedCommand):
    async def run(self) -> None:
        account_names = [account.name for account in self.profile_data.watched_accounts]
        typer.echo(str(account_names))
