from typing import Optional

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import ProfileOptionsGroup
from clive.__private.cli.common.parameters import argument_related_options
from clive.__private.cli.common.parameters.ensure_single_value import EnsureSingleValue
from clive.__private.core.constants.cli import REQUIRED_AS_ARG_OR_OPTION

chain_id = CliveTyper(name="chain-id", help="Manage the chain ID for the profile.")

_chain_id_argument = typer.Argument(
    None,
    help=(f"The chain ID to use when signing the transaction. ({REQUIRED_AS_ARG_OR_OPTION})"),
    show_default=False,
)


@chain_id.command(name="set", param_groups=[ProfileOptionsGroup])
async def set_chain_id(
    ctx: typer.Context,  # noqa: ARG001
    chain_id: Optional[str] = _chain_id_argument,
    chain_id_option: Optional[str] = argument_related_options.chain_id,
) -> None:
    """
    Set/change the chain ID for the profile.

    If not set, the one from node get_config api will be retrieved and set.
    """
    from clive.__private.cli.commands.configure.chain_id import SetChainId

    common = ProfileOptionsGroup.get_instance()
    await SetChainId(**common.as_dict(), chain_id=EnsureSingleValue("chain-id").of(chain_id, chain_id_option)).run()


@chain_id.command(name="unset", param_groups=[ProfileOptionsGroup])
async def unset_chain_id(
    ctx: typer.Context,  # noqa: ARG001
) -> None:
    """
    Unset the actual chain ID for the profile.

    Will be dynamically set to the one from node get_config api when needed first time.
    """
    from clive.__private.cli.commands.configure.chain_id import UnsetChainId

    common = ProfileOptionsGroup.get_instance()
    await UnsetChainId(**common.as_dict()).run()
