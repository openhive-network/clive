from typing import Optional

import typer

from clive.__private.cli.commands.beekeeper import BeekeeperInfo
from clive.__private.cli.common.options import beekeeper_remote_option
from clive.__private.cli.common.with_beekeeper import WithBeekeeper

beekeeper = typer.Typer(help="Beekeeper-related commands.")


@beekeeper.command()
@WithBeekeeper.decorator
def info(
    ctx: typer.Context,
    beekeeper_remote: Optional[str] = beekeeper_remote_option,  # noqa: ARG001
) -> None:
    """Show the beekeeper info."""
    common = WithBeekeeper(**ctx.params)
    BeekeeperInfo(beekeeper=common.beekeeper).run()
