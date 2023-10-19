from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.beekeeper_based_command import BeekeeperBasedCommand
from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.cli.commands.abc.profile_based_command import ProfileBasedCommand
from clive.__private.cli.commands.accounts import AccountsList
from clive.__private.cli_error import CLIPrettyError
from clive.__private.core.commands.create_wallet import CreateWallet
from clive.__private.core.profile_data import ProfileAlreadyExistsError, ProfileData, ProfileDoesNotExistsError
from clive.core.url import Url
from clive.exceptions import CommunicationError


@dataclass(kw_only=True)
class ProfileShow(AccountsList):
    async def run(self) -> None:
        self._show_profile_info()
        self._show_accounts_info()

    def _show_profile_info(self) -> None:
        profile = self.profile_data
        typer.echo(f"Profile name: {profile.name}")
        typer.echo(f"Node address: {profile.node_address}")
        typer.echo(f"Backup node addresses: {[str(url) for url in profile.backup_node_addresses]}")


@dataclass(kw_only=True)
class ProfileList(ExternalCLICommand):
    async def run(self) -> None:
        typer.echo(f"Stored profiles are: {ProfileData.list_profiles()}")


@dataclass(kw_only=True)
class ProfileCreate(BeekeeperBasedCommand):
    profile_name: str
    password: str

    async def run(self) -> None:
        profile = ProfileData(self.profile_name)

        try:
            profile.save()
        except ProfileAlreadyExistsError as error:
            raise CLIPrettyError(str(error)) from None

        try:
            await CreateWallet(beekeeper=self.beekeeper, wallet=profile.name, password=self.password).execute()
        except CommunicationError as error:
            profile.delete()
            raise CLIPrettyError(str(error)) from None


@dataclass(kw_only=True)
class ProfileDelete(ExternalCLICommand):
    profile_name: str

    async def run(self) -> None:
        try:
            ProfileData.delete_by_name(self.profile_name)
        except ProfileDoesNotExistsError as error:
            raise CLIPrettyError(str(error)) from None


@dataclass(kw_only=True)
class ProfileSetNode(ProfileBasedCommand):
    node_address: str

    async def run(self) -> None:
        url = Url.parse(self.node_address)
        self.profile_data._set_node_address(url)
