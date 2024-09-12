import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import BeekeeperOptionsGroup

beekeeper = CliveTyper(name="beekeeper", help="Beekeeper-related commands.")


@beekeeper.command(param_groups=[BeekeeperOptionsGroup])
async def info(ctx: typer.Context) -> None:  # noqa: ARG001
    """Show the beekeeper info."""
    from clive.__private.cli.commands.beekeeper import BeekeeperInfo

    common = BeekeeperOptionsGroup.get_instance()
    await BeekeeperInfo(**common.as_dict()).run()


@beekeeper.command()
async def spawn(
    background: bool = typer.Option(default=True, help="Run in background."),  # noqa: FBT001
) -> None:
    """Spawn beekeeper process."""
    from clive.__private.cli.commands.beekeeper import BeekeeperSpawn

    await BeekeeperSpawn(background=background).run()


@beekeeper.command()
async def close() -> None:
    """Close beekeeper process."""
    from clive.__private.cli.commands.beekeeper import BeekeeperClose

    await BeekeeperClose().run()
