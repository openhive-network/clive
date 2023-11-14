import typer

from clive.__private.cli.common.with_profile import WithProfile

node = typer.Typer(name="node", help="Manage the node for the profile.")


@node.command(name="set")
@WithProfile.decorator
async def set_node(
    ctx: typer.Context,
    node_address: str = typer.Option(..., help="The address of the node to use.", show_default=False),
) -> None:
    """Set the node address for the profile."""
    from clive.__private.cli.commands.configure.node import SetNode

    common = WithProfile(**ctx.params)
    await SetNode(**common.dict(), node_address=node_address).run()
