from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.cli.commands.abc.profile_based_command import ProfileBasedCommand
from clive.__private.cli_error import CLIError
from clive.__private.core.profile_data import ProfileAlreadyExistsError, ProfileData


@dataclass(kw_only=True)
class ProfileShow(ProfileBasedCommand):
    async def run(self) -> None:
        profile = self._load_profile()
        typer.echo(f"Profile is: {profile.name}")

        if profile.is_working_account_set():
            typer.echo(f"Working account: {profile.working_account.name}")
        else:
            typer.echo("Working account is not set.")
        typer.echo(f"Watched accounts: {[account.name for account in profile.watched_accounts]}")
        typer.echo(f"Known accounts: {[account.name for account in profile.known_accounts]}")


@dataclass(kw_only=True)
class ProfileList(ExternalCLICommand):
    async def run(self) -> None:
        typer.echo(f"Stored profiles are: {ProfileData.list_profiles()}")


@dataclass(kw_only=True)
class ProfileCreate(ExternalCLICommand):
    name: str

    async def run(self) -> None:
        try:
            ProfileData(self.name).save()
        except ProfileAlreadyExistsError as error:
            raise CLIError(str(error)) from None
