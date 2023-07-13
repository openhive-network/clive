import typer

spawn = typer.Typer(help="Spawn some process.")


@spawn.command()
def beekeeper(
    background: bool = typer.Option(True, help="Run in background."),
) -> None:
    """Spawn beekeeper process."""
    from clive.__private.cli.commands.spawn import SpawnBeekeeper

    SpawnBeekeeper(background=background).run()
