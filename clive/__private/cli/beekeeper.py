from typing import Optional

import typer

from clive.__private.cli.common import options
from clive.__private.cli.common.with_beekeeper import WithBeekeeper
from clive.__private.core._async import asyncio_run

beekeeper = typer.Typer(help="Beekeeper-related commands.")


@beekeeper.command()
@WithBeekeeper.decorator
async def info(
    ctx: typer.Context,
    beekeeper_remote: Optional[str] = options.beekeeper_remote_option,  # noqa: ARG001
) -> None:
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
