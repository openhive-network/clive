from __future__ import annotations

from typing import TYPE_CHECKING, cast

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options

if TYPE_CHECKING:
    from clive.__private.models.asset import Asset

rc_delegations = CliveTyper(
    name="rc-delegations", help="Delegate or revoke resource credits. Requires posting authority."
)

_delegatee_account_name = typer.Option(
    ...,
    "--delegatee",
    help="The account to delegate RC to.",
)


@rc_delegations.command(name="set")
async def process_rc_delegations_set(  # noqa: PLR0913
    account_name: str = options.account_name,
    delegatee: str = _delegatee_account_name,
    amount: str = options.voting_amount,
    sign_with: list[str] = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
    force: bool = options.force,  # noqa: FBT001
) -> None:
    """Delegate resource credits to another account. Requires posting authority."""
    from clive.__private.cli.commands.process.process_rc_delegations import ProcessRcDelegation  # noqa: PLC0415

    amount_ = cast("Asset.VotingT", amount)
    operation = ProcessRcDelegation(
        from_account=account_name,
        delegatee=delegatee,
        amount=amount_,
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
        force=force,
    )
    await operation.run()


@rc_delegations.command(name="remove")
async def process_rc_delegations_remove(  # noqa: PLR0913
    account_name: str = options.account_name,
    delegatee: str = _delegatee_account_name,
    sign_with: list[str] = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Revoke RC delegation from an account (sets delegated RC to zero). Requires posting authority."""
    from clive.__private.cli.commands.process.process_rc_delegations import ProcessRcDelegationRemove  # noqa: PLC0415

    operation = ProcessRcDelegationRemove(
        from_account=account_name,
        delegatee=delegatee,
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    )
    await operation.run()
