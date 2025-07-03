from __future__ import annotations

from typing import TYPE_CHECKING, cast

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options

if TYPE_CHECKING:
    from clive.__private.models import Asset

delegations = CliveTyper(name="delegations", help="Set or remove vesting delegaton.")

_delegatee_account_name = typer.Option(
    ...,
    "--delegatee",
    help='The account to use as "delegatee" argument.',
    show_default=False,
)


@delegations.command(name="set")
async def process_delegations_set(  # noqa: PLR0913
    account_name: str = options.account_name,
    delegatee: str = _delegatee_account_name,
    amount: str = options.voting_amount,
    sign: str | None = options.sign,
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
    force: bool = options.force_value,  # noqa: FBT001
) -> None:
    """
    Add or modify vesting shares delegation for pair of accounts "account-name" and "delegatee".

    Args:
        account_name: The name of the delegator account.
        delegatee: The name of the delegatee account.
        amount: The amount of vesting shares to delegate, in the format "X HIVE" or "X HBD".
        sign: Optional, if provided, the operation will be signed with the working account.
        broadcast: If True, the operation will be broadcasted to the network.
        save_file: If provided, the operation will be saved to this file instead of broadcasting it.
        force: If True, force the delegation even if it might not be optimal.

    Returns:
        None
    """
    from clive.__private.cli.commands.process.process_delegations import ProcessDelegations

    amount_ = cast("Asset.VotingT", amount)
    operation = ProcessDelegations(
        delegator=account_name,
        delegatee=delegatee,
        amount=amount_,
        sign=sign,
        broadcast=broadcast,
        save_file=save_file,
        force=force,
    )
    await operation.run()


@delegations.command(name="remove")
async def process_delegations_remove(
    account_name: str = options.account_name,
    delegatee: str = _delegatee_account_name,
    sign: str | None = options.sign,
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """
    Clear vesting shares delegation (by setting it to zero) for pair of accounts "account-name" and "delegatee".

    Args:
        account_name: The name of the delegator account.
        delegatee: The name of the delegatee account.
        sign: Optional, if provided, the operation will be signed with the working account.
        broadcast: If True, the operation will be broadcasted to the network.
        save_file: If provided, the operation will be saved to this file instead of broadcasting it.

    Returns:
        None
    """
    from clive.__private.cli.commands.process.process_delegations import ProcessDelegationsRemove

    operation = ProcessDelegationsRemove(
        delegator=account_name,
        delegatee=delegatee,
        sign=sign,
        broadcast=broadcast,
        save_file=save_file,
    )
    await operation.run()
