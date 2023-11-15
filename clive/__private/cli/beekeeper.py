import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common.beekeeper_common_options import BeekeeperCommonOptions

beekeeper = CliveTyper(name="beekeeper", help="Beekeeper-related commands.")


@beekeeper.command(common_options=[BeekeeperCommonOptions])
async def info(ctx: typer.Context) -> None:  # noqa: ARG001
    """Show the beekeeper info."""
    from clive.__private.cli.commands.beekeeper import BeekeeperInfo

    common = BeekeeperCommonOptions.get_instance()
    await BeekeeperInfo(**common.as_dict()).run()


@beekeeper.command()
async def spawn(
    background: bool = typer.Option(True, help="Run in background."),
) -> None:
    """Spawn beekeeper process."""
    from clive.__private.cli.commands.beekeeper import BeekeeperSpawn

    await BeekeeperSpawn(background=background).run()


@beekeeper.command()
async def close() -> None:
    """Close beekeeper process."""
    from clive.__private.cli.commands.beekeeper import BeekeeperClose

    await BeekeeperClose().run()
