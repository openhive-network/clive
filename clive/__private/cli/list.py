import typer

from clive.__private.cli.common import options
from clive.__private.cli.common.with_profile import WithProfile
from clive.__private.cli.common.with_world import WithWorld
from clive.__private.core._async import asyncio_run

list_ = typer.Typer(name="list", help="List various things.")


@list_.command()
def profiles() -> None:
    """List all stored profiles."""
    from clive.__private.cli.commands.list import ListProfiles

    asyncio_run(ListProfiles().run())


@list_.command()
@WithProfile.decorator
async def keys(ctx: typer.Context) -> None:
    """List all Public keys stored in the wallet."""
    from clive.__private.cli.commands.list import ListKeys

    common = WithProfile(**ctx.params)
    await ListKeys(profile_data=common.profile_data).run()


@list_.command()
@WithProfile.decorator
async def node(ctx: typer.Context) -> None:
    """List address of the currently selected node."""
    from clive.__private.cli.commands.list import ListNode

    common = WithProfile(**ctx.params)
    await ListNode(profile_data=common.profile_data).run()


@list_.command()
@WithWorld.decorator(use_beekeeper=False)
async def balances(ctx: typer.Context, account_name: str = options.account_name_option) -> None:
    """List balances of the currently selected account."""
    from clive.__private.cli.commands.list import ListBalances

    common = WithWorld(**ctx.params)
    await ListBalances(world=common.world, account_name=account_name).run()


@list_.command()
@WithWorld.decorator(use_beekeeper=False)
async def transaction_status(
    ctx: typer.Context,
    transaction_id: str = typer.Option(..., help="Hash of transaction.", show_default=False),
) -> None:
    """Print status of transaction given as argument."""
    from clive.__private.cli.commands.list import ListTransactionStatus

    common = WithWorld(**ctx.params)
    await ListTransactionStatus(world=common.world, transaction_id=transaction_id).run()
