import time
from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.core.beekeeper import Beekeeper
from clive.__private.core.exit_call_handler import ExitCallHandler


@dataclass
class SpawnBeekeeper(ExternalCLICommand):
    def run(self) -> None:
        typer.echo("Launching beekeeper...")

        with ExitCallHandler(Beekeeper(), finally_callback=lambda bk: bk.close()) as beekeeper:
            beekeeper.start()

            typer.echo(f"Beekeeper started on {beekeeper.http_endpoint}. Press Ctrl+C to exit.")

            while True:
                time.sleep(1)
