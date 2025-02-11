from enum import Enum
from typing import Optional, cast

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import WorldOptionsGroup
from clive.__private.cli.common.parameters import argument_related_options, arguments, options
from clive.__private.cli.common.parameters.ensure_single_value import (
    EnsureSingleAccountNameValue,
    EnsureSingleValue,
)
from clive.__private.cli.common.parameters.modified_param import modified_param
from clive.__private.cli.completion import is_tab_completion_active
from clive.__private.cli.show.pending import pending
from clive.__private.core.constants.cli import REQUIRED_AS_ARG_OR_OPTION

show = CliveTyper(name="show", help="Show various data.")

show.add_typer(pending)


@show.command("profiles")
async def show_profiles() -> None:
    """Show all stored profiles."""
    from clive.__private.cli.commands.show.show_profiles import ShowProfiles

    await ShowProfiles().run()


@show.command(name="profile", param_groups=[WorldOptionsGroup])
async def show_profile(ctx: typer.Context) -> None:  # noqa: ARG001
    """Show profile information."""
    from clive.__private.cli.commands.show.show_profile import ShowProfile

    common = WorldOptionsGroup.get_instance()
    await ShowProfile(**common.as_dict()).run()


@show.command(name="accounts", param_groups=[WorldOptionsGroup])
async def show_accounts(ctx: typer.Context) -> None:  # noqa: ARG001
    """Show all accounts stored in the profile."""
    from clive.__private.cli.commands.show.show_accounts import ShowAccounts

    common = WorldOptionsGroup.get_instance()
    await ShowAccounts(**common.as_dict()).run()


@show.command(name="keys", param_groups=[WorldOptionsGroup])
async def show_keys(ctx: typer.Context) -> None:  # noqa: ARG001
    """Show all the public keys stored in Clive."""
    from clive.__private.cli.commands.show.show_keys import ShowKeys

    common = WorldOptionsGroup.get_instance()
    await ShowKeys(**common.as_dict()).run()


@show.command(name="balances", param_groups=[WorldOptionsGroup])
async def show_balances(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = arguments.account_name,
    account_name_option: Optional[str] = argument_related_options.account_name,
) -> None:
    """Show balances of the selected account."""
    from clive.__private.cli.commands.show.show_balances import ShowBalances

    common = WorldOptionsGroup.get_instance()
    await ShowBalances(
        **common.as_dict(), account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)
    ).run()


@show.command(name="node", param_groups=[WorldOptionsGroup])
async def show_node(ctx: typer.Context) -> None:  # noqa: ARG001
    """Show address of the currently selected node."""
    from clive.__private.cli.commands.show.show_node import ShowNode

    common = WorldOptionsGroup.get_instance()
    await ShowNode(**common.as_dict()).run()


_transaction_id_argument = typer.Argument(
    None, help=f"Hash of the transaction ({REQUIRED_AS_ARG_OR_OPTION}).", show_default=False
)


@show.command(name="transaction-status", param_groups=[WorldOptionsGroup])
async def show_transaction_status(
    ctx: typer.Context,  # noqa: ARG001
    transaction_id: Optional[str] = _transaction_id_argument,
    transaction_id_option: Optional[str] = argument_related_options.transaction_id,
) -> None:
    """Print status of a specific transaction."""
    from clive.__private.cli.commands.show.show_transaction_status import ShowTransactionStatus

    common = WorldOptionsGroup.get_instance()
    await ShowTransactionStatus(
        **common.as_dict(), transaction_id=EnsureSingleValue("transaction-id").of(transaction_id, transaction_id_option)
    ).run()


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
        "OrdersEnum", {option: option for option in ProposalsDataRetrieval.ORDERS}
    )
    OrderDirectionsEnum = Enum(  # type: ignore[misc, no-redef]
        "OrderDirectionsEnum", {option: option for option in ProposalsDataRetrieval.ORDER_DIRECTIONS}
    )
    StatusesEnum = Enum(  # type: ignore[misc, no-redef]
        "StatusesEnum", {option: option for option in ProposalsDataRetrieval.STATUSES}
    )

    DEFAULT_ORDER = ProposalsDataRetrieval.DEFAULT_ORDER
    DEFAULT_ORDER_DIRECTION = ProposalsDataRetrieval.DEFAULT_ORDER_DIRECTION
    DEFAULT_STATUS = ProposalsDataRetrieval.DEFAULT_STATUS


@show.command(name="proxy", param_groups=[WorldOptionsGroup])
async def show_proxy(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = arguments.account_name,
    account_name_option: Optional[str] = argument_related_options.account_name,
) -> None:
    """Show proxy of selected account."""
    from clive.__private.cli.commands.show.show_proxy import ShowProxy

    common = WorldOptionsGroup.get_instance()
    await ShowProxy(
        **common.as_dict(),
        account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option),
    ).run()


witnesses_page_size = modified_param(
    options.page_size, default=30, help="The number of witnesses presented on a single page."
)
witnesses_page_no = modified_param(
    options.page_no, help="Page number of the witnesses list, considering the given page size."
)


@show.command(name="witnesses", param_groups=[WorldOptionsGroup])
async def show_witnesses(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = arguments.account_name,
    account_name_option: Optional[str] = argument_related_options.account_name,
    page_size: int = witnesses_page_size,
    page_no: int = witnesses_page_no,
) -> None:
    """List witnesses and votes of selected account."""
    from clive.__private.cli.commands.show.show_witnesses import ShowWitnesses

    common = WorldOptionsGroup.get_instance()
    await ShowWitnesses(
        **common.as_dict(),
        account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option),
        page_size=page_size,
        page_no=page_no,
    ).run()


_witness_name_argument = typer.Argument(None, help=f"Witness name. ({REQUIRED_AS_ARG_OR_OPTION})", show_default=False)


@show.command(name="witness", param_groups=[WorldOptionsGroup])
async def show_witness(
    ctx: typer.Context,  # noqa: ARG001
    name: Optional[str] = _witness_name_argument,
    name_option: Optional[str] = argument_related_options.name,
) -> None:
    """Show details of a specified witness."""
    from clive.__private.cli.commands.show.show_witness import ShowWitness

    common = WorldOptionsGroup.get_instance()
    await ShowWitness(
        **common.as_dict(),
        name=EnsureSingleValue("name").of(name, name_option),
    ).run()


proposals_page_size = modified_param(options.page_size, help="The number of proposals presented on a single page.")
proposals_page_no = modified_param(
    options.page_no, help="Page number of the proposals list, considering the given page size."
)


@show.command(name="proposals", param_groups=[WorldOptionsGroup])
async def show_proposals(  # noqa: PLR0913
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = arguments.account_name,
    account_name_option: Optional[str] = argument_related_options.account_name,
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
    page_size: int = proposals_page_size,
    page_no: int = proposals_page_no,
) -> None:
    """List proposals filtered by status."""
    from clive.__private.cli.commands.show.show_proposals import ShowProposals

    assert isinstance(order_by, Enum), f"Expected Enum type, but got: {type(order_by)}"
    assert isinstance(order_direction, Enum), f"Expected Enum type, but got: {type(order_by)}"
    assert isinstance(status, Enum), f"Expected Enum type, but got: {type(order_by)}"

    order_by_ = cast(ProposalsDataRetrieval.Orders, order_by.value)
    order_direction_ = cast(ProposalsDataRetrieval.OrderDirections, order_direction.value)
    status_ = cast(ProposalsDataRetrieval.Statuses, status.value)

    common = WorldOptionsGroup.get_instance()
    await ShowProposals(
        **common.as_dict(),
        account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option),
        order_by=order_by_,
        order_direction=order_direction_,
        status=status_,
        page_size=page_size,
        page_no=page_no,
    ).run()


_proposal_id_argument = typer.Argument(
    None,
    help=f"Identifier of chosen proposal. ({REQUIRED_AS_ARG_OR_OPTION})",
    show_default=False,
)


@show.command(name="proposal", param_groups=[WorldOptionsGroup])
async def show_proposal(
    ctx: typer.Context,  # noqa: ARG001
    proposal_id: Optional[int] = _proposal_id_argument,
    proposal_id_option: Optional[int] = argument_related_options.proposal_id,
) -> None:
    """Show details of a specified proposal."""
    from clive.__private.cli.commands.show.show_proposal import ShowProposal

    common = WorldOptionsGroup.get_instance()
    await ShowProposal(
        **common.as_dict(),
        proposal_id=EnsureSingleValue[int]("proposal-id").of(proposal_id, proposal_id_option),
    ).run()


@show.command(name="owner-authority", param_groups=[WorldOptionsGroup])
async def show_owner_authority(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = arguments.account_name,
    account_name_option: Optional[str] = argument_related_options.account_name,
) -> None:
    """Fetch from blockchain and display owner authority of selected account."""
    from clive.__private.cli.commands.show.show_authority import ShowAuthority

    common = WorldOptionsGroup.get_instance()
    await ShowAuthority(
        **common.as_dict(),
        account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option),
        authority="owner",
    ).run()


@show.command(name="active-authority", param_groups=[WorldOptionsGroup])
async def show_active_authority(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = arguments.account_name,
    account_name_option: Optional[str] = argument_related_options.account_name,
) -> None:
    """Fetch from blockchain and display active authority of selected account."""
    from clive.__private.cli.commands.show.show_authority import ShowAuthority

    common = WorldOptionsGroup.get_instance()
    await ShowAuthority(
        **common.as_dict(),
        account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option),
        authority="active",
    ).run()


@show.command(name="posting-authority", param_groups=[WorldOptionsGroup])
async def show_posting_authority(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = arguments.account_name,
    account_name_option: Optional[str] = argument_related_options.account_name,
) -> None:
    """Fetch from blockchain and display posting authority of selected account."""
    from clive.__private.cli.commands.show.show_authority import ShowAuthority

    common = WorldOptionsGroup.get_instance()
    await ShowAuthority(
        **common.as_dict(),
        account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option),
        authority="posting",
    ).run()


@show.command(name="memo-key", param_groups=[WorldOptionsGroup])
async def show_memo_key(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = arguments.account_name,
    account_name_option: Optional[str] = argument_related_options.account_name,
) -> None:
    """Fetch from blockchain and display memo key of selected account."""
    from clive.__private.cli.commands.show.show_memo_key import ShowMemoKey

    common = WorldOptionsGroup.get_instance()
    await ShowMemoKey(
        **common.as_dict(), account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)
    ).run()


@show.command(name="chain", param_groups=[WorldOptionsGroup])
async def show_chain(ctx: typer.Context) -> None:  # noqa: ARG001
    """Fetch from blockchain and display chain info."""
    from clive.__private.cli.commands.show.show_chain import ShowChain

    common = WorldOptionsGroup.get_instance()
    await ShowChain(**common.as_dict()).run()


@show.command(name="hive-power", param_groups=[WorldOptionsGroup])
async def show_hive_power(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = arguments.account_name,
    account_name_option: Optional[str] = argument_related_options.account_name,
) -> None:
    """Show info about hive power related to account including delegations and withdraw routes."""
    from clive.__private.cli.commands.show.show_hive_power import ShowHivePower

    common = WorldOptionsGroup.get_instance()
    await ShowHivePower(
        **common.as_dict(), account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)
    ).run()


@show.command(name="new-account-token", param_groups=[WorldOptionsGroup])
async def show_new_account_token(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = arguments.account_name,
    account_name_option: Optional[str] = argument_related_options.account_name,
) -> None:
    """
    Show number of possessed tokens for account creation.

    To get account creation fee use command `clive show chain`.
    """
    from clive.__private.cli.commands.show.show_new_account_token import ShowNewAccountToken

    common = WorldOptionsGroup.get_instance()
    await ShowNewAccountToken(
        **common.as_dict(), account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)
    ).run()


@show.command(name="transfer-schedule", param_groups=[WorldOptionsGroup])
async def show_transfer_schedule(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = arguments.account_name,
    account_name_option: Optional[str] = argument_related_options.account_name,
) -> None:
    """Fetch from blockchain information about recurrent transfers of selected account."""
    from clive.__private.cli.commands.show.show_transfer_schedule import ShowTransferSchedule

    common = WorldOptionsGroup.get_instance()
    await ShowTransferSchedule(
        **common.as_dict(), account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)
    ).run()


@show.command(name="account", param_groups=[WorldOptionsGroup])
async def show_account(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = arguments.account_name,
    account_name_option: Optional[str] = argument_related_options.account_name,
) -> None:
    """Show information about given account."""
    from clive.__private.cli.commands.show.show_account import ShowAccount

    common = WorldOptionsGroup.get_instance()
    await ShowAccount(
        **common.as_dict(), account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)
    ).run()
