from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.core.profile import Profile


@dataclass(kw_only=True)
class ShowProfiles(ExternalCLICommand):
    async def _run(self) -> None:
        typer.echo(f"Stored profiles are: {Profile.list_profiles()}")
