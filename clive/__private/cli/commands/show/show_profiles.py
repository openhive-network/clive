from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.core.profile_data import ProfileData


@dataclass(kw_only=True)
class ShowProfiles(ExternalCLICommand):
    async def _run(self) -> None:
        typer.echo(f"Stored profiles are: {ProfileData.list_profiles()}")
