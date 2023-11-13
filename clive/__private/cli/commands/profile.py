from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.cli.commands.accounts import AccountsList
from clive.__private.core.profile_data import ProfileData


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
