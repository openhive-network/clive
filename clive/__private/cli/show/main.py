import typing
from enum import Enum

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options
from clive.__private.cli.common.profile_common_options import ProfileCommonOptions
from clive.__private.cli.common.world_common_options import WorldWithoutBeekeeperCommonOptions
from clive.__private.cli.completion import is_tab_completion_active
from clive.__private.cli.show.pending import pending

show = CliveTyper(name="show", help="Show various data.")

show.add_typer(pending)


@show.command("profiles")
async def show_profiles() -> None:
    """Show all stored profiles."""
    from clive.__private.cli.commands.show.show_profiles import ShowProfiles

    await ShowProfiles().run()


@show.command(name="profile", common_options=[ProfileCommonOptions])
async def show_profile(ctx: typer.Context) -> None:  # noqa: ARG001
    """Show profile information."""
    from clive.__private.cli.commands.show.show_profile import ShowProfile

    common = ProfileCommonOptions.get_instance()
    await ShowProfile(**common.as_dict()).run()


@show.command(name="accounts", common_options=[ProfileCommonOptions])
async def show_accounts(ctx: typer.Context) -> None:  # noqa: ARG001
    """Show all accounts stored in the profile."""
    from clive.__private.cli.commands.show.show_accounts import ShowAccounts

    common = ProfileCommonOptions.get_instance()
    await ShowAccounts(**common.as_dict()).run()


@show.command(name="keys", common_options=[ProfileCommonOptions])
async def show_keys(ctx: typer.Context) -> None:  # noqa: ARG001
    """Show all the public keys stored in Clive."""
    from clive.__private.cli.commands.show.show_keys import ShowKeys

    common = ProfileCommonOptions.get_instance()
    await ShowKeys(**common.as_dict()).run()


@show.command(name="balances", common_options=[WorldWithoutBeekeeperCommonOptions])
async def show_balances(ctx: typer.Context, account_name: str = options.account_name_option) -> None:  # noqa: ARG001
    """Show balances of the selected account."""
    from clive.__private.cli.commands.show.show_balances import ShowBalances

    common = WorldWithoutBeekeeperCommonOptions.get_instance()
    await ShowBalances(**common.as_dict(), account_name=account_name).run()


@show.command(name="node", common_options=[ProfileCommonOptions])
async def show_node(ctx: typer.Context) -> None:  # noqa: ARG001
    """Show address of the currently selected node."""
    from clive.__private.cli.commands.show.show_node import ShowNode

    common = ProfileCommonOptions.get_instance()
    await ShowNode(**common.as_dict()).run()


@show.command(name="transaction-status", common_options=[WorldWithoutBeekeeperCommonOptions])
async def show_transaction_status(
    ctx: typer.Context,  # noqa: ARG001
    transaction_id: str = typer.Option(..., help="Hash of the transaction.", show_default=False),
) -> None:
    """Print status of a specific transaction."""
    from clive.__private.cli.commands.show.show_transaction_status import ShowTransactionStatus

    common = WorldWithoutBeekeeperCommonOptions.get_instance()
    await ShowTransactionStatus(**common.as_dict(), transaction_id=transaction_id).run()


if is_tab_completion_active():
    OrdersEnum = str
    OrderDirectionsEnum = str
    StatusesEnum = str
    DEFAULT_ORDER = ""  # doesn't matter, won't be shown anyway
    DEFAULT_ORDER_DIRECTION = ""
    DEFAULT_STATUS = ""
else:
    from clive.__private.core.commands.data_retrieval.proposals_data import ProposalsDataRetrieval

    # unfortunately typer doesn't support Literal types yet, so we have to convert it to an enum
    OrdersEnum = Enum(  # type: ignore[misc, no-redef]
        "OrdersEnum", {option: option for option in typing.get_args(ProposalsDataRetrieval.Orders)}
    )
    OrderDirectionsEnum = Enum(  # type: ignore[misc, no-redef]
        "OrderDirectionsEnum", {option: option for option in typing.get_args(ProposalsDataRetrieval.OrderDirections)}
    )
    StatusesEnum = Enum(  # type: ignore[misc, no-redef]
        "StatusesEnum", {option: option for option in typing.get_args(ProposalsDataRetrieval.Statuses)}
    )

    DEFAULT_ORDER = ProposalsDataRetrieval.DEFAULT_ORDER
    DEFAULT_ORDER_DIRECTION = ProposalsDataRetrieval.DEFAULT_ORDER_DIRECTION
    DEFAULT_STATUS = ProposalsDataRetrieval.DEFAULT_STATUS


@show.command(name="proposals", common_options=[WorldWithoutBeekeeperCommonOptions])
async def show_proposal(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = options.account_name_option,
    order_by: OrdersEnum = typer.Option(
        DEFAULT_ORDER,
        help="Proposals listing can be ordered by criteria.",
    ),
    order_direction: OrderDirectionsEnum = typer.Option(
        DEFAULT_ORDER_DIRECTION,
        help="Proposals listing direction.",
    ),
    status: StatusesEnum = typer.Option(
        DEFAULT_STATUS,
        help="Proposals can be filtered by status.",
    ),
    page_size: int = typer.Option(
        10,
        help="Number of proposals in one listing.",
    ),
    page_no: int = typer.Option(
        0,
        help="Index of proposals list considering given page size.",
    ),
) -> None:
    """List proposals filtered by status."""
    from clive.__private.cli.commands.show.show_proposals import ShowProposals

    if isinstance(order_by, Enum):
        order_by = order_by.value
    if isinstance(order_direction, Enum):
        order_direction = order_direction.value
    if isinstance(status, Enum):
        status = status.value

    common = WorldWithoutBeekeeperCommonOptions.get_instance()
    await ShowProposals(
        **common.as_dict(),
        account_name=account_name,
        order_by=order_by,
        order_direction=order_direction,
        status=status,
        page_size=page_size,
        page_no=page_no,
    ).run()


@show.command(name="proxy", common_options=[WorldWithoutBeekeeperCommonOptions])
async def show_proxy(ctx: typer.Context, account_name: str = options.account_name_option) -> None:  # noqa: ARG001
    """Show proxy of selected account."""
    from clive.__private.cli.commands.show.show_proxy import ShowProxy

    common = WorldWithoutBeekeeperCommonOptions.get_instance()
    await ShowProxy(**common.as_dict(), account_name=account_name).run()


@show.command(name="witnesses", common_options=[WorldWithoutBeekeeperCommonOptions])
async def show_witnesses(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = options.account_name_option,
    page_size: int = typer.Option(
        30,
        help="Number of witnesses in one listing.",
    ),
    page_no: int = typer.Option(
        0,
        help="Index of witnesses list considering given page size.",
    ),
) -> None:
    """List witnesses and votes of selected account."""
    from clive.__private.cli.commands.show.show_witnesses import ShowWitnesses

    common = WorldWithoutBeekeeperCommonOptions.get_instance()
    await ShowWitnesses(
        **common.as_dict(),
        account_name=account_name,
        page_size=page_size,
        page_no=page_no,
    ).run()


@show.command(name="witness", common_options=[WorldWithoutBeekeeperCommonOptions])
async def show_witness(
    ctx: typer.Context,  # noqa: ARG001
    name: str = typer.Option(
        ...,
        help="Witness name.",
    ),
) -> None:
    """Shows details of witness."""
    from clive.__private.cli.commands.show.show_witness import ShowWitness

    common = WorldWithoutBeekeeperCommonOptions.get_instance()
    await ShowWitness(
        **common.as_dict(),
        name=name,
    ).run()
