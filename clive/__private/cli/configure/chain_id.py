import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common.profile_common_options import ProfileCommonOptions

chain_id = CliveTyper(name="chain-id", help="Manage the chain ID for the profile.")


@chain_id.command(name="set", common_options=[ProfileCommonOptions])
async def set_chain_id(
    ctx: typer.Context,  # noqa: ARG001
    chain_id_: str = typer.Option(
        ...,
        "--chain-id",
        help=(
            "The chain ID to use when signing the transaction. (if not provided, the one from node get_config "
            "api will be set)"
        ),
        show_default=False,
    ),
) -> None:
    """Set/change the chain ID for the profile."""
    from clive.__private.cli.commands.configure.chain_id import SetChainId

    common = ProfileCommonOptions.get_instance()
    await SetChainId(**common.as_dict(), chain_id=chain_id_).run()


@chain_id.command(name="unset", common_options=[ProfileCommonOptions])
async def unset_chain_id(
    ctx: typer.Context,  # noqa: ARG001
) -> None:
    """Unset the actual chain ID for the profile. Will be dynamically set to the one from node get_config api when needed first time."""
    from clive.__private.cli.commands.configure.chain_id import UnsetChainId

    common = ProfileCommonOptions.get_instance()
    await UnsetChainId(**common.as_dict()).run()
