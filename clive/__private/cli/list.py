import typer

from clive.__private.cli.common import options
from clive.__private.cli.common.with_world import WithWorld

list_ = typer.Typer(help="List various things.")


@list_.command()
@WithWorld.decorator(use_beekeeper=False)
async def keys(
    ctx: typer.Context,
) -> None:
    """List all Public keys stored in the wallet."""
    from clive.__private.cli.commands.list import ListKeys

    common = WithWorld(**ctx.params)
    await ListKeys(world=common.world).run()


@list_.command()
@WithWorld.decorator(use_beekeeper=False)
async def node(
    ctx: typer.Context,
) -> None:
    """List address of the currently selected node."""
    from clive.__private.cli.commands.list import ListNode

    common = WithWorld(**ctx.params)
    await ListNode(world=common.world).run()


@list_.command()
@WithWorld.decorator(use_beekeeper=False)
async def balances(ctx: typer.Context, account_name: str = options.account_name_option) -> None:
    """List balances of the currently selected account."""
    from clive.__private.cli.commands.list import ListBalances

    common = WithWorld(**ctx.params)
    await ListBalances(world=common.world, account_name=account_name).run()
