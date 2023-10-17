from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.cli.commands.accounts import AccountsList
from clive.__private.cli_error import CLIError
from clive.__private.core.profile_data import ProfileAlreadyExistsError, ProfileData


@dataclass(kw_only=True)
class ProfileShow(AccountsList):
    pass


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
