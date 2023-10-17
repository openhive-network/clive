from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.cli.commands.abc.profile_based_command import ProfileBasedCommand
from clive.__private.cli.commands.accounts import AccountsList
from clive.__private.cli_error import CLIError
from clive.__private.core.profile_data import ProfileAlreadyExistsError, ProfileData
from clive.core.url import Url


@dataclass(kw_only=True)
class ProfileShow(AccountsList):
    async def run(self) -> None:
        self._show_profile_info()
        self._show_accounts_info()

    def _show_profile_info(self) -> None:
        profile = self.profile_data
        typer.echo(f"Node address: {profile._node_address}")
        typer.echo(f"Backup node addresses: {[str(url) for url in profile.backup_node_addresses]}")


@dataclass(kw_only=True)
class ProfileList(ExternalCLICommand):
    async def run(self) -> None:
        typer.echo(f"Stored profiles are: {ProfileData.list_profiles()}")


@dataclass(kw_only=True)
class ProfileCreate(ExternalCLICommand):
    profile_name: str

    async def run(self) -> None:
        try:
            ProfileData(self.profile_name).save()
        except ProfileAlreadyExistsError as error:
            raise CLIError(str(error)) from None


@dataclass(kw_only=True)
class ProfileSetNode(ProfileBasedCommand):
    node_address: str

    async def run(self) -> None:
        url = Url.parse(self.node_address)
        self.profile_data._node_address = url
