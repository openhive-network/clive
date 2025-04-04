from typing import TYPE_CHECKING, Optional, cast

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import OperationOptionsGroup, options

if TYPE_CHECKING:
    from clive.__private.models import Asset

savings = CliveTyper(name="savings", help="Manage your savings.")


@savings.command(name="deposit", param_groups=[OperationOptionsGroup])
async def process_deposit(
    ctx: typer.Context,  # noqa: ARG001
    from_account: str = options.from_account_name,
    to_account: str = options.to_account_name,
    amount: str = options.liquid_amount,
    memo: str = options.memo_value,
) -> None:
    """Immediately deposit funds to savings account."""
    from clive.__private.cli.commands.process.process_deposit import ProcessDeposit

    operation_common = OperationOptionsGroup.get_instance()
    amount_ = cast("Asset.LiquidT", amount)

    await ProcessDeposit(
        **operation_common.as_dict(),
        from_account=from_account,
        to_account=to_account,
        amount=amount_,
        memo=memo,
    ).run()


@savings.command(name="withdrawal", param_groups=[OperationOptionsGroup])
async def process_withdrawal(  # noqa: PLR0913
    ctx: typer.Context,  # noqa: ARG001
    from_account: str = options.from_account_name,
    to_account: str = options.to_account_name,
    amount: str = options.liquid_amount,
    memo: str = options.memo_value,
    request_id: Optional[int] = typer.Option(
        None,
        help="Id of new withdrawal. (if not given, will be automatically calculated)",
        show_default=False,
    ),
) -> None:
    """Initiate withdrawal of funds from savings account, it takes 3 days to complete."""
    from clive.__private.cli.commands.process.process_withdrawal import ProcessWithdrawal

    operation_common = OperationOptionsGroup.get_instance()
    amount_ = cast("Asset.LiquidT", amount)
    await ProcessWithdrawal(
        **operation_common.as_dict(),
        from_account=from_account,
        to_account=to_account,
        amount=amount_,
        memo=memo,
        request_id=request_id,
    ).run()


@savings.command(name="withdrawal-cancel", param_groups=[OperationOptionsGroup])
async def process_withdrawal_cancel(
    ctx: typer.Context,  # noqa: ARG001
    from_account: str = options.from_account_name,
    request_id: int = typer.Option(..., help="Id of previously initiated withdrawal.", show_default=False),
) -> None:
    """Cancel previously initiated withdrawal from savings account."""
    from clive.__private.cli.commands.process.process_withdrawal_cancel import ProcessWithdrawalCancel

    operation_common = OperationOptionsGroup.get_instance()
    await ProcessWithdrawalCancel(
        **operation_common.as_dict(),
        from_account=from_account,
        request_id=request_id,
    ).run()
