import time

import typer

from clive.__private.core.beekeeper import Beekeeper
from clive.__private.util import ExitCallHandler

spawn = typer.Typer(help="Spawn some process.")


@spawn.command()
def beekeeper() -> None:
    """Spawn beekeeper process."""
    typer.echo("Launching beekeeper...")

    with ExitCallHandler(Beekeeper(), finally_callback=lambda bk: bk.close()) as beekeeper:
        beekeeper.start()

        typer.echo(f"Beekeeper started on {beekeeper.http_endpoint}. Press Ctrl+C to exit.")

        while True:
            time.sleep(1)
