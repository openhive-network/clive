from __future__ import annotations

from enum import Enum
from typing import cast

import typer

from clive.__private.cli.clive_typer import CliveTyper
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
    """
    Show all stored profiles.

    Returns:
        None: This function does not return any value. It runs the ShowProfiles command to display profile information.
    """
    from clive.__private.cli.commands.show.show_profiles import ShowProfiles

    await ShowProfiles().run()


@show.command(name="profile")
async def show_profile() -> None:
    """
    Show profile information.

    Returns:
        None: This function does not return any value. It runs the ShowProfile command to display profile details.
    """
    from clive.__private.cli.commands.show.show_profile import ShowProfile

    await ShowProfile().run()


@show.command(name="accounts")
async def show_accounts() -> None:
    """
    Show all accounts stored in the profile.

    Returns:
        None: This function does not return any value. It runs the ShowAccounts command to display account information.
    """
    from clive.__private.cli.commands.show.show_accounts import ShowAccounts

    await ShowAccounts().run()


@show.command(name="keys")
async def show_keys() -> None:
    """
    Show all the public keys stored in Clive.

    Returns:
        None: This function does not return any value. It runs the ShowKeys command to display keys.
    """
    from clive.__private.cli.commands.show.show_keys import ShowKeys

    await ShowKeys().run()


@show.command(name="balances")
async def show_balances(
    account_name: str = arguments.account_name,
    account_name_option: str | None = argument_related_options.account_name,
) -> None:
    """
    Show balances of the selected account.

    Args:
        account_name: Name of the account to show balances for.
        account_name_option: Optional argument for account name, if not provided will use the default.

    Returns:
        None: This function does not return any value. It runs the ShowBalances command to display account balances.
    """
    from clive.__private.cli.commands.show.show_balances import ShowBalances

    await ShowBalances(account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)).run()


@show.command(name="node")
async def show_node() -> None:
    """
    Show address of the currently selected node.

    Returns:
        None: This function does not return any value. It runs the ShowNode command to display node information.
    """
    from clive.__private.cli.commands.show.show_node import ShowNode

    await ShowNode().run()


_transaction_id_argument = typer.Argument(
    None, help=f"Hash of the transaction ({REQUIRED_AS_ARG_OR_OPTION}).", show_default=False
)


@show.command(name="transaction-status")
async def show_transaction_status(
    transaction_id: str | None = _transaction_id_argument,
    transaction_id_option: str | None = argument_related_options.transaction_id,
) -> None:
    """
    Print status of a specific transaction.

    Args:
        transaction_id: The ID of the transaction to show status for.
        transaction_id_option: Optional argument for transaction ID, if not provided will use the default.

    Returns:
        None: Runs the ShowTransactionStatus command to display transaction status.
    """
    from clive.__private.cli.commands.show.show_transaction_status import ShowTransactionStatus

    await ShowTransactionStatus(
        transaction_id=EnsureSingleValue("transaction-id").of(transaction_id, transaction_id_option)
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


@show.command(name="proxy")
async def show_proxy(
    account_name: str = arguments.account_name,
    account_name_option: str | None = argument_related_options.account_name,
) -> None:
    """
    Show proxy of selected account.

    Args:
        account_name: Name of the account to show proxy for.
        account_name_option: Optional argument for account name, if not provided will use the default.

    Returns:
        None: This function does not return any value. It runs the ShowProxy command to display proxy information.
    """
    from clive.__private.cli.commands.show.show_proxy import ShowProxy

    await ShowProxy(
        account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option),
    ).run()


witnesses_page_size = modified_param(
    options.page_size, default=30, help="The number of witnesses presented on a single page."
)
witnesses_page_no = modified_param(
    options.page_no, help="Page number of the witnesses list, considering the given page size."
)


@show.command(name="witnesses")
async def show_witnesses(
    account_name: str = arguments.account_name,
    account_name_option: str | None = argument_related_options.account_name,
    page_size: int = witnesses_page_size,
    page_no: int = witnesses_page_no,
) -> None:
    """
    List witnesses and votes of selected account.

    Args:
        account_name: Name of the account to show witnesses for.
        account_name_option: Optional argument for account name, if not provided will use the default.
        page_size: Number of witnesses to display per page.
        page_no: Page number of the witnesses list, considering the given page size.

    Returns:
        None: This function does not return any value. It runs the ShowWitnesses command to display witness information.
    """
    from clive.__private.cli.commands.show.show_witnesses import ShowWitnesses

    await ShowWitnesses(
        account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option),
        page_size=page_size,
        page_no=page_no,
    ).run()


_witness_name_argument = typer.Argument(None, help=f"Witness name. ({REQUIRED_AS_ARG_OR_OPTION})", show_default=False)


@show.command(name="witness")
async def show_witness(
    name: str | None = _witness_name_argument,
    name_option: str | None = argument_related_options.name,
) -> None:
    """
    Show details of a specified witness.

    Args:
        name: Name of the witness to show details for.
        name_option: Optional argument for witness name, if not provided will use the default.

    Returns:
        None: This function does not return any value. It runs the ShowWitness command to display witness details.
    """
    from clive.__private.cli.commands.show.show_witness import ShowWitness

    await ShowWitness(
        name=EnsureSingleValue("name").of(name, name_option),
    ).run()


proposals_page_size = modified_param(options.page_size, help="The number of proposals presented on a single page.")
proposals_page_no = modified_param(
    options.page_no, help="Page number of the proposals list, considering the given page size."
)


@show.command(name="proposals")
async def show_proposals(  # noqa: PLR0913
    account_name: str = arguments.account_name,
    account_name_option: str | None = argument_related_options.account_name,
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
    """
    List proposals filtered by status.

    Args:
        account_name: Name of the account to show proposals for.
        account_name_option: Optional argument for account name, if not provided will use the default.
        order_by: Criteria to order the proposals list.
        order_direction: Direction to order the proposals list.
        status: Status to filter the proposals list.
        page_size: Number of proposals to display per page.
        page_no: Page number of the proposals list, considering the given page size.

    Returns:
        None: This function does not return any value. It runs the ShowProposals command to display proposals.
    """
    from clive.__private.cli.commands.show.show_proposals import ShowProposals

    assert isinstance(order_by, Enum), f"Expected Enum type, but got: {type(order_by)}"
    assert isinstance(order_direction, Enum), f"Expected Enum type, but got: {type(order_by)}"
    assert isinstance(status, Enum), f"Expected Enum type, but got: {type(order_by)}"

    order_by_ = cast("ProposalsDataRetrieval.Orders", order_by.value)
    order_direction_ = cast("ProposalsDataRetrieval.OrderDirections", order_direction.value)
    status_ = cast("ProposalsDataRetrieval.Statuses", status.value)

    await ShowProposals(
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


@show.command(name="proposal")
async def show_proposal(
    proposal_id: int | None = _proposal_id_argument,
    proposal_id_option: int | None = argument_related_options.proposal_id,
) -> None:
    """
    Show details of a specified proposal.

    Args:
        proposal_id: Identifier of the proposal to show details for.
        proposal_id_option: Optional argument for proposal ID, if not provided will use the default.

    Returns:
        None: This function does not return any value. It runs the ShowProposal command to display proposal details.
    """
    from clive.__private.cli.commands.show.show_proposal import ShowProposal

    await ShowProposal(
        proposal_id=EnsureSingleValue[int]("proposal-id").of(proposal_id, proposal_id_option),
    ).run()


@show.command(name="owner-authority")
async def show_owner_authority(
    account_name: str = arguments.account_name,
    account_name_option: str | None = argument_related_options.account_name,
) -> None:
    """
    Fetch from blockchain and display owner authority of selected account.

    Args:
        account_name: Name of the account to show owner authority for.
        account_name_option: Optional argument for account name, if not provided will use the default.

    Returns:
        None: This function does not return any value. It runs the ShowAuthority command to display owner authority.
    """
    from clive.__private.cli.commands.show.show_authority import ShowAuthority

    await ShowAuthority(
        account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option),
        authority="owner",
    ).run()


@show.command(name="active-authority")
async def show_active_authority(
    account_name: str = arguments.account_name,
    account_name_option: str | None = argument_related_options.account_name,
) -> None:
    """
    Fetch from blockchain and display active authority of selected account.

    Args:
        account_name: Name of the account to show active authority for.
        account_name_option: Optional argument for account name, if not provided will use the default.

    Returns:
        None: This function does not return any value. It runs the ShowAuthority command to display active authority.
    """
    from clive.__private.cli.commands.show.show_authority import ShowAuthority

    await ShowAuthority(
        account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option),
        authority="active",
    ).run()


@show.command(name="posting-authority")
async def show_posting_authority(
    account_name: str = arguments.account_name,
    account_name_option: str | None = argument_related_options.account_name,
) -> None:
    """
    Fetch from blockchain and display posting authority of selected account.

    Args:
        account_name: Name of the account to show posting authority for.
        account_name_option: Optional argument for account name, if not provided will use the default.

    Returns:
        None: This function does not return any value. It runs the ShowAuthority command to display posting authority.
    """
    from clive.__private.cli.commands.show.show_authority import ShowAuthority

    await ShowAuthority(
        account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option),
        authority="posting",
    ).run()


@show.command(name="memo-key")
async def show_memo_key(
    account_name: str = arguments.account_name,
    account_name_option: str | None = argument_related_options.account_name,
) -> None:
    """
    Fetch from blockchain and display memo key of selected account.

    Args:
        account_name: Name of the account to show memo key for.
        account_name_option: Optional argument for account name, if not provided will use the default.

    Returns:
        None: This function does not return any value. It runs the ShowMemoKey command to display memo key.
    """
    from clive.__private.cli.commands.show.show_memo_key import ShowMemoKey

    await ShowMemoKey(account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)).run()


@show.command(name="chain")
async def show_chain() -> None:
    """
    Fetch from blockchain and display chain info.

    Returns:
        None: This function does not return any value. It runs the ShowChain command to display chain information.
    """
    from clive.__private.cli.commands.show.show_chain import ShowChain

    await ShowChain().run()


@show.command(name="hive-power")
async def show_hive_power(
    account_name: str = arguments.account_name,
    account_name_option: str | None = argument_related_options.account_name,
) -> None:
    """
    Show info about hive power related to account including delegations and withdraw routes.

    Args:
        account_name: Name of the account to show hive power for.
        account_name_option: Optional argument for account name, if not provided will use the default.

    Returns:
        None: It runs the ShowHivePower command to display hive power information.
    """
    from clive.__private.cli.commands.show.show_hive_power import ShowHivePower

    await ShowHivePower(account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)).run()


@show.command(name="new-account-token")
async def show_new_account_token(
    account_name: str = arguments.account_name,
    account_name_option: str | None = argument_related_options.account_name,
) -> None:
    """
    Show number of possessed tokens for account creation.

    To get account creation fee use command `clive show chain`.

    Args:
        account_name: Name of the account to show new account token for.
        account_name_option: Optional argument for account name, if not provided will use the default.

    Returns:
        None: It runs the ShowNewAccountToken command to display new account token information.
    """
    from clive.__private.cli.commands.show.show_new_account_token import ShowNewAccountToken

    await ShowNewAccountToken(account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)).run()


@show.command(name="transfer-schedule")
async def show_transfer_schedule(
    account_name: str = arguments.account_name,
    account_name_option: str | None = argument_related_options.account_name,
) -> None:
    """
    Fetch from blockchain information about recurrent transfers of selected account.

    Args:
        account_name: Name of the account to show transfer schedule for.
        account_name_option: Optional argument for account name, if not provided will use the default.

    Returns:
        None: It runs the ShowTransferSchedule command to display transfer schedule information.
    """
    from clive.__private.cli.commands.show.show_transfer_schedule import ShowTransferSchedule

    await ShowTransferSchedule(account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)).run()


@show.command(name="account")
async def show_account(
    account_name: str = arguments.account_name,
    account_name_option: str | None = argument_related_options.account_name,
) -> None:
    """
    Show information about given account.

    Args:
        account_name: Name of the account to show information for.
        account_name_option: Optional argument for account name, if not provided will use the default.

    Returns:
        None: It runs the ShowAccount command to display account information.
    """
    from clive.__private.cli.commands.show.show_account import ShowAccount

    await ShowAccount(account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)).run()
