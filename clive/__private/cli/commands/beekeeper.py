import time
from dataclasses import dataclass
from pathlib import Path

import typer
from beekeepy import beekeeper_factory, close_already_running_beekeeper

from clive.__private.cli.commands.abc.beekeeper_based_command import BeekeeperBasedCommand
from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.config import settings
from clive.models.aliased import Settings


def _get_beekeeper_directory() -> Path:
    return Path(settings.get("data_path")) / "beekeeper"


@dataclass(kw_only=True)
class BeekeeperInfo(BeekeeperBasedCommand):
    async def _run(self) -> None:
        typer.echo((await self.session.get_info()).json(by_alias=True))


@dataclass(kw_only=True)
class BeekeeperSpawn(ExternalCLICommand):
    background: bool

    async def _run(self) -> None:
        beekeeper_factory(settings=Settings(working_directory=_get_beekeeper_directory()))
        if not self.background:
            self.__serve_forever()

    @staticmethod
    def __serve_forever() -> None:
        typer.echo("Press Ctrl+C to exit.")

        while True:
            time.sleep(1)


@dataclass(kw_only=True)
class BeekeeperClose(ExternalCLICommand):
    async def _run(self) -> None:
        close_already_running_beekeeper(working_directory=_get_beekeeper_directory())
