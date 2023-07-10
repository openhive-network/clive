import typer

spawn = typer.Typer(help="Spawn some process.")


@spawn.command()
def beekeeper() -> None:
    """Spawn beekeeper process."""
    from clive.__private.cli.commands.spawn import SpawnBeekeeper

    SpawnBeekeeper().run()
