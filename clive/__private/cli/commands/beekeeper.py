from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.core.beekeeper import Beekeeper


@dataclass(kw_only=True)
class BeekeeperInfo(ExternalCLICommand):
    beekeeper: Beekeeper

    def run(self) -> None:
        typer.echo(self.beekeeper.api.get_info().json(by_alias=True))
