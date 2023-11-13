import typer

from clive.__private.cli.common.with_world import WithWorld

list_ = typer.Typer(name="list", help="List various things.")


@list_.command()
@WithWorld.decorator(use_beekeeper=False)
async def transaction_status(
    ctx: typer.Context,
    transaction_id: str = typer.Option(..., help="Hash of transaction.", show_default=False),
) -> None:
    """Print status of a specific transaction."""
    from clive.__private.cli.commands.list import ListTransactionStatus

    common = WithWorld(**ctx.params)
    await ListTransactionStatus(world=common.world, transaction_id=transaction_id).run()
