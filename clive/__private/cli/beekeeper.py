from typing import Optional

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
async def import_key(
    ctx: typer.Context,
    key: str = typer.Option(
        ..., help="The key to import. This can be a path to a file or a key itself.", show_default=False
    ),
    alias: Optional[str] = typer.Option(
        None,
        help="The alias to use for the key. (If not given, calculated public key will be used)",
        show_default=False,
    ),
    password: str = options.password_option,
    beekeeper_remote: Optional[str] = options.beekeeper_remote_option,  # noqa: ARG001 # used in WithWorld
) -> None:
    """Import a key into the Beekeeper, and make it ready to use for Clive."""
    from clive.__private.cli.commands.beekeeper import BeekeeperImportKey

    common = WithWorld(**ctx.params)
    await BeekeeperImportKey(world=common.world, password=password, key_or_path=key, alias=alias).run()
