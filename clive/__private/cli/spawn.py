import typer

from clive.__private.cli.commands.spawn import SpawnBeekeeper

spawn = typer.Typer(help="Spawn some process.")


@spawn.command()
def beekeeper() -> None:
    """Spawn beekeeper process."""
    SpawnBeekeeper().run()
