from __future__ import annotations

from typing import TYPE_CHECKING, cast

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options

if TYPE_CHECKING:
    from clive.__private.models.asset import Asset

savings = CliveTyper(name="savings", help="Manage your savings.")


@savings.command(name="deposit")
async def process_deposit(  # noqa: PLR0913
    from_account: str = options.from_account_name,
    to_account: str = options.to_account_name,
    amount: str = options.liquid_amount,
    memo: str = options.memo,
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
    force: bool = options.force,  # noqa: FBT001
) -> None:
    """Immediately deposit funds to savings account."""
    from clive.__private.cli.commands.process.process_deposit import ProcessDeposit  # noqa: PLC0415

    amount_ = cast("Asset.LiquidT", amount)

    await ProcessDeposit(
        from_account=from_account,
        to_account=to_account,
        amount=amount_,
        memo=memo,
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        force=force,
        autosign=autosign,
    ).run()


@savings.command(name="withdrawal")
async def process_withdrawal(  # noqa: PLR0913
    from_account: str = options.from_account_name,
    to_account: str = options.to_account_name,
    amount: str = options.liquid_amount,
    memo: str = options.memo,
    request_id: int | None = typer.Option(
        None,
        help="Id of new withdrawal. (if not given, will be automatically calculated)",
    ),
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
    force: bool = options.force,  # noqa: FBT001
) -> None:
    """Initiate withdrawal of funds from savings account, it takes 3 days to complete."""
    from clive.__private.cli.commands.process.process_withdrawal import ProcessWithdrawal  # noqa: PLC0415

    amount_ = cast("Asset.LiquidT", amount)
    await ProcessWithdrawal(
        from_account=from_account,
        to_account=to_account,
        amount=amount_,
        memo=memo,
        request_id=request_id,
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        force=force,
        autosign=autosign,
    ).run()


@savings.command(name="withdrawal-cancel")
async def process_withdrawal_cancel(  # noqa: PLR0913
    from_account: str = options.from_account_name,
    request_id: int = typer.Option(..., help="Id of previously initiated withdrawal."),
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Cancel previously initiated withdrawal from savings account."""
    from clive.__private.cli.commands.process.process_withdrawal_cancel import ProcessWithdrawalCancel  # noqa: PLC0415

    await ProcessWithdrawalCancel(
        from_account=from_account,
        request_id=request_id,
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    ).run()
