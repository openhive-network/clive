from typing import Optional

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common.parameters.ensure_single_value import ensure_single_value
from clive.__private.cli.common.parameters.utils import make_argument_related_option
from clive.__private.cli.common.profile_common_options import ProfileCommonOptions

node = CliveTyper(name="node", help="Manage the node for the profile.")

_node_address_argument = typer.Argument(
    None,
    help="The address of the node to use.",
    show_default=False,
)


@node.command(name="set", common_options=[ProfileCommonOptions])
async def set_node(
    ctx: typer.Context,  # noqa: ARG001
    node_address: Optional[str] = _node_address_argument,
    node_address_option: Optional[str] = make_argument_related_option("--node-address"),
) -> None:
    """Set the node address for the profile."""
    from clive.__private.cli.commands.configure.node import SetNode

    common = ProfileCommonOptions.get_instance()
    await SetNode(
        **common.as_dict(), node_address=ensure_single_value(node_address, node_address_option, "node-address")
    ).run()
