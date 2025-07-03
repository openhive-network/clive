from __future__ import annotations

from typing import TYPE_CHECKING, cast

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options

if TYPE_CHECKING:
    from clive.__private.models import Asset

savings = CliveTyper(name="savings", help="Manage your savings.")


@savings.command(name="deposit")
async def process_deposit(  # noqa: PLR0913
    from_account: str = options.from_account_name,
    to_account: str = options.to_account_name,
    amount: str = options.liquid_amount,
    memo: str = options.memo_value,
    sign: str | None = options.sign,
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
    force: bool = options.force_value,  # noqa: FBT001
) -> None:
    """
    Immediately deposit funds to savings account.

    Args:
        from_account: The account from which the funds are being deposited.
        to_account: The savings account to which the funds are being deposited.
        amount: The amount of funds to deposit, in liquid asset format.
        memo: An optional memo for the transaction.
        sign: Optional signature for the transaction.
        broadcast: Whether to broadcast the transaction immediately.
        save_file: Optional file path to save the transaction details.
        force: Whether to force the operation, bypassing certain checks.

    Returns:
        None: This function does not return a value; it executes the deposit process.
    """
    from clive.__private.cli.commands.process.process_deposit import ProcessDeposit

    amount_ = cast("Asset.LiquidT", amount)

    await ProcessDeposit(
        from_account=from_account,
        to_account=to_account,
        amount=amount_,
        memo=memo,
        sign=sign,
        broadcast=broadcast,
        save_file=save_file,
        force=force,
    ).run()


@savings.command(name="withdrawal")
async def process_withdrawal(  # noqa: PLR0913
    from_account: str = options.from_account_name,
    to_account: str = options.to_account_name,
    amount: str = options.liquid_amount,
    memo: str = options.memo_value,
    request_id: int | None = typer.Option(
        None,
        help="Id of new withdrawal. (if not given, will be automatically calculated)",
        show_default=False,
    ),
    sign: str | None = options.sign,
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
    force: bool = options.force_value,  # noqa: FBT001
) -> None:
    """
    Initiate withdrawal of funds from savings account, it takes 3 days to complete.

    Args:
        from_account: The account from which the funds are being withdrawn.
        to_account: The account to which the funds are being sent.
        amount: The amount of funds to withdraw, in liquid asset format.
        memo: An optional memo for the transaction.
        request_id: Optional ID for the withdrawal request; if not provided, it will be calculated automatically.
        sign: Optional signature for the transaction.
        broadcast: Whether to broadcast the transaction immediately.
        save_file: Optional file path to save the transaction details.
        force: Whether to force the operation, bypassing certain checks.

    Returns:
        None: This function does not return a value; it executes the withdrawal process.
    """
    from clive.__private.cli.commands.process.process_withdrawal import ProcessWithdrawal

    amount_ = cast("Asset.LiquidT", amount)
    await ProcessWithdrawal(
        from_account=from_account,
        to_account=to_account,
        amount=amount_,
        memo=memo,
        request_id=request_id,
        sign=sign,
        broadcast=broadcast,
        save_file=save_file,
        force=force,
    ).run()


@savings.command(name="withdrawal-cancel")
async def process_withdrawal_cancel(
    from_account: str = options.from_account_name,
    request_id: int = typer.Option(..., help="Id of previously initiated withdrawal.", show_default=False),
    sign: str | None = options.sign,
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """
    Cancel previously initiated withdrawal from savings account.

    Args:
        from_account: The account from which the withdrawal is being canceled.
        request_id: The ID of the previously initiated withdrawal to cancel.
        sign: Optional signature for the transaction.
        broadcast: Whether to broadcast the transaction immediately.
        save_file: Optional file path to save the transaction details.

    Returns:
        None: This function does not return a value; it executes the withdrawal cancellation process.
    """
    from clive.__private.cli.commands.process.process_withdrawal_cancel import ProcessWithdrawalCancel

    await ProcessWithdrawalCancel(
        from_account=from_account,
        request_id=request_id,
        sign=sign,
        broadcast=broadcast,
        save_file=save_file,
    ).run()
