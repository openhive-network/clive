import typer

from clive.__private.cli.common import WithWorld, options
from clive.__private.cli.common.with_beekeeper import WithBeekeeper
from clive.__private.core._async import asyncio_run

beekeeper = typer.Typer(name="beekeeper", help="Beekeeper-related commands.")


@beekeeper.command()
@WithBeekeeper.decorator
async def info(ctx: typer.Context) -> None:
    """Show the beekeeper info."""
    from clive.__private.cli.commands.beekeeper import BeekeeperInfo

    common = WithBeekeeper(**ctx.params)
    await BeekeeperInfo(beekeeper=common.beekeeper).run()


@beekeeper.command()
def spawn(
    background: bool = typer.Option(True, help="Run in background."),
) -> None:
    """Spawn beekeeper process."""
    from clive.__private.cli.commands.beekeeper import BeekeeperSpawn

    asyncio_run(BeekeeperSpawn(background=background).run())


@beekeeper.command()
def close() -> None:
    """Close beekeeper process."""
    from clive.__private.cli.commands.beekeeper import BeekeeperClose

    asyncio_run(BeekeeperClose().run())


@beekeeper.command()
@WithWorld.decorator()
async def sync(
    ctx: typer.Context,
    password: str = options.password_option,
) -> None:
    """Sync data with the Beekeeper."""
    from clive.__private.cli.commands.beekeeper import BeekeeperSync

    common = WithWorld(**ctx.params)
    await BeekeeperSync(world=common.world, password=password).run()
