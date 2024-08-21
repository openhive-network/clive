from typing import TYPE_CHECKING, cast

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import OperationCommonOptions, options

if TYPE_CHECKING:
    from clive.__private.models import Asset

delegations = CliveTyper(name="delegations", help="Set or remove vesting delegaton.")


@delegations.command(name="set", common_options=[OperationCommonOptions])
async def process_delegations_set(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = options.account_name_option,
    delegatee: str = options.delegatee_account_name_option,
    amount: str = options.voting_amount_option,
) -> None:
    """Add or modify vesting shares delegation for pair of accounts "account-name" and "delegatee"."""
    from clive.__private.cli.commands.process.process_delegations import ProcessDelegations

    common = OperationCommonOptions.get_instance()
    amount_ = cast("Asset.VotingT", amount)
    operation = ProcessDelegations(**common.as_dict(), delegator=account_name, delegatee=delegatee, amount=amount_)
    await operation.run()


@delegations.command(name="remove", common_options=[OperationCommonOptions])
async def process_delegations_remove(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = options.account_name_option,
    delegatee: str = options.delegatee_account_name_option,
) -> None:
    """Clear vesting shares delegation (by setting it to zero) for pair of accounts "account-name" and "delegatee"."""
    from clive.__private.cli.commands.process.process_delegations import ProcessDelegationsRemove

    common = OperationCommonOptions.get_instance()
    operation = ProcessDelegationsRemove(**common.as_dict(), delegator=account_name, delegatee=delegatee)
    await operation.run()
