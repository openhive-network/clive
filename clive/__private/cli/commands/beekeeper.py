import time
from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.core.beekeeper import Beekeeper
from clive.__private.core.exit_call_handler import ExitCallHandler


@dataclass(kw_only=True)
class BeekeeperInfo(ExternalCLICommand):
    beekeeper: Beekeeper

    def run(self) -> None:
        typer.echo(self.beekeeper.api.get_info().json(by_alias=True))


@dataclass(kw_only=True)
class BeekeeperSpawn(ExternalCLICommand):
    background: bool

    def run(self) -> None:
        typer.echo("Launching beekeeper...")

        with ExitCallHandler(
            Beekeeper(run_in_background=self.background),
            finally_callback=lambda bk: bk.close() if not self.background else None,
        ) as beekeeper:
            beekeeper.start()

            typer.echo(f"Beekeeper started on {beekeeper.http_endpoint} with pid {beekeeper.pid}.")

            if not self.background:
                self.__serve_forever()

    @staticmethod
    def __serve_forever() -> None:
        typer.echo("Press Ctrl+C to exit.")

        while True:
            time.sleep(1)
