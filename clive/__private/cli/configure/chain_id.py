from typing import Optional

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common.ensure_single_value import ensure_single_value
from clive.__private.cli.common.parameters.utils import make_argument_related_option
from clive.__private.cli.common.profile_common_options import ProfileCommonOptions
from clive.__private.core.constants.cli import REQUIRED_AS_ARG_OR_OPTION

chain_id = CliveTyper(name="chain-id", help="Manage the chain ID for the profile.")

_chain_id_argument = typer.Argument(
    None,
    help=(f"The chain ID to use when signing the transaction. ({REQUIRED_AS_ARG_OR_OPTION})"),
    show_default=False,
)


@chain_id.command(name="set", common_options=[ProfileCommonOptions])
async def set_chain_id(
    ctx: typer.Context,  # noqa: ARG001
    chain_id: Optional[str] = _chain_id_argument,
    chain_id_option: Optional[str] = make_argument_related_option("--chain-id"),
) -> None:
    """
    Set/change the chain ID for the profile.

    If not set, the one from node get_config api will be retrieved and set.
    """
    from clive.__private.cli.commands.configure.chain_id import SetChainId

    common = ProfileCommonOptions.get_instance()
    await SetChainId(**common.as_dict(), chain_id=ensure_single_value(chain_id, chain_id_option, "chain-id")).run()


@chain_id.command(name="unset", common_options=[ProfileCommonOptions])
async def unset_chain_id(
    ctx: typer.Context,  # noqa: ARG001
) -> None:
    """
    Unset the actual chain ID for the profile.

    Will be dynamically set to the one from node get_config api when needed first time.
    """
    from clive.__private.cli.commands.configure.chain_id import UnsetChainId

    common = ProfileCommonOptions.get_instance()
    await UnsetChainId(**common.as_dict()).run()
