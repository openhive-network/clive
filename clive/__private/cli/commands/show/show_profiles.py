from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.storage.service import PersistentStorageService


@dataclass(kw_only=True)
class ShowProfiles(ExternalCLICommand):
    async def _run(self) -> None:
        typer.echo(f"Stored profiles are: {PersistentStorageService.list_stored_profile_names()}")
