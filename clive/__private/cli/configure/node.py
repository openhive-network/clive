from __future__ import annotations

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common.parameters import argument_related_options
from clive.__private.cli.common.parameters.ensure_single_value import EnsureSingleValue

node = CliveTyper(name="node", help="Manage the node for the profile.")

_node_address_argument = typer.Argument(
    None,
    help="The address of the node to use.",
    show_default=False,
)


@node.command(name="set")
async def set_node(
    node_address: str | None = _node_address_argument,
    node_address_option: str | None = argument_related_options.node_address,
) -> None:
    """
    Set the node address for the profile.

    Args:
        node_address: The address of the node to use.
        node_address_option: An alternative way to specify the node address.

    Returns:
        None
    """
    from clive.__private.cli.commands.configure.node import SetNode

    await SetNode(node_address=EnsureSingleValue("node-address").of(node_address, node_address_option)).run()
