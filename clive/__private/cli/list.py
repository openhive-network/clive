import typer

from clive.__private.cli.commands.list import ListKeys, ListNode
from clive.__private.cli.common.with_world import WithWorld

list_ = typer.Typer(help="List various things.")


@list_.command()
@WithWorld.decorator(use_beekeeper=False)
def keys(
    ctx: typer.Context,
) -> None:
    """
    List all Public keys stored in the wallet.
    """
    common = WithWorld(**ctx.params)
    ListKeys(world=common.world).run()


@list_.command()
@WithWorld.decorator(use_beekeeper=False)
def node(
    ctx: typer.Context,
) -> None:
    """List address of the currently selected node."""
    common = WithWorld(**ctx.params)
    ListNode(world=common.world).run()
