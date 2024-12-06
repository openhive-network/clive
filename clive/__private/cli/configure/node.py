from typing import Optional

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import WorldOptionsGroup
from clive.__private.cli.common.parameters import argument_related_options
from clive.__private.cli.common.parameters.ensure_single_value import EnsureSingleValue

node = CliveTyper(name="node", help="Manage the node for the profile.")

_node_address_argument = typer.Argument(
    None,
    help="The address of the node to use.",
    show_default=False,
)


@node.command(name="set", param_groups=[WorldOptionsGroup])
async def set_node(
    ctx: typer.Context,  # noqa: ARG001
    node_address: Optional[str] = _node_address_argument,
    node_address_option: Optional[str] = argument_related_options.node_address,
) -> None:
    """Set the node address for the profile."""
    from clive.__private.cli.commands.configure.node import SetNode

    common = WorldOptionsGroup.get_instance()
    await SetNode(
        **common.as_dict(), node_address=EnsureSingleValue("node-address").of(node_address, node_address_option)
    ).run()
