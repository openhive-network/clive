import typer

from clive.__private.cli.common import WithWorld, options
from clive.__private.cli.common.with_profile import WithProfile
from clive.__private.core._async import asyncio_run

show = typer.Typer(name="show", help="Show various data.")


@show.command(name="profiles")
def show_profiles() -> None:
    """Show all stored profiles."""
    from clive.__private.cli.commands.show.show_profiles import ShowProfiles

    asyncio_run(ShowProfiles().run())


@show.command(name="accounts")
@WithProfile.decorator
async def show_accounts(ctx: typer.Context) -> None:
    """Show all accounts stored in the profile."""
    from clive.__private.cli.commands.show.show_accounts import ShowAccounts

    common = WithProfile(**ctx.params)
    await ShowAccounts(profile_data=common.profile_data).run()


@show.command(name="keys")
@WithProfile.decorator
async def show_keys(ctx: typer.Context) -> None:
    """Show all the public keys stored in Clive."""
    from clive.__private.cli.commands.show.show_keys import ShowKeys

    common = WithProfile(**ctx.params)
    await ShowKeys(profile_data=common.profile_data).run()


@show.command(name="balances")
@WithWorld.decorator(use_beekeeper=False)
async def show_balances(ctx: typer.Context, account_name: str = options.account_name_option) -> None:
    """Show balances of the selected account."""
    from clive.__private.cli.commands.show.show_balances import ShowBalances

    common = WithWorld(**ctx.params)
    await ShowBalances(world=common.world, account_name=account_name).run()


@show.command(name="node")
@WithProfile.decorator
async def show_node(ctx: typer.Context) -> None:
    """Show address of the currently selected node."""
    from clive.__private.cli.commands.show.show_node import ShowNode

    common = WithProfile(**ctx.params)
    await ShowNode(profile_data=common.profile_data).run()


@show.command(name="transaction-status")
@WithProfile.decorator
async def show_transaction_status(
    ctx: typer.Context,
    transaction_id: str = typer.Option(..., help="Hash of the transaction.", show_default=False),
) -> None:
    """Print status of a specific transaction."""
    from clive.__private.cli.commands.show.show_transaction_status import ShowTransactionStatus

    common = WithProfile(**ctx.params)
    await ShowTransactionStatus(**common.dict(), transaction_id=transaction_id).run()
