from typing import Optional

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import OperationCommonOptions, TransferCommonOptions, options

savings = CliveTyper(name="savings", help="Manage your savings.")


@savings.command(name="deposit", common_options=[OperationCommonOptions, TransferCommonOptions])
async def process_deposit(
    ctx: typer.Context,  # noqa: ARG001
    to_account: str = options.to_account_name_option,
) -> None:
    """Immediately deposit funds to savings account."""
    from clive.__private.cli.commands.process.process_deposit import ProcessDeposit

    operation_common = OperationCommonOptions.get_instance()
    transfer_common = TransferCommonOptions.get_instance()
    await ProcessDeposit(
        **operation_common.as_dict(),
        **transfer_common.as_dict(),
        to_account=to_account,
    ).run()


@savings.command(name="withdrawal", common_options=[OperationCommonOptions, TransferCommonOptions])
async def process_withdrawal(
    ctx: typer.Context,  # noqa: ARG001
    request_id: Optional[int] = typer.Option(
        None,
        help="Id of new withdrawal. (if not given, will be automatically calculated)",
        show_default=False,
    ),
    to_account: str = options.to_account_name_option,
) -> None:
    """Initiate withdrawal of funds from savings account, it takes 3 days to complete."""
    from clive.__private.cli.commands.process.process_withdrawal import ProcessWithdrawal

    operation_common = OperationCommonOptions.get_instance()
    transfer_common = TransferCommonOptions.get_instance()
    await ProcessWithdrawal(
        **operation_common.as_dict(),
        **transfer_common.as_dict(),
        request_id=request_id,
        to_account=to_account,
    ).run()


@savings.command(name="withdrawal-cancel", common_options=[OperationCommonOptions])
async def process_withdrawal_cancel(
    ctx: typer.Context,  # noqa: ARG001
    from_account: str = options.from_account_name_option,
    request_id: int = typer.Option(..., help="Id of previously initiated withdrawal.", show_default=False),
) -> None:
    """Cancel previously initiated withdrawal from savings account."""
    from clive.__private.cli.commands.process.process_withdrawal_cancel import ProcessWithdrawalCancel

    operation_common = OperationCommonOptions.get_instance()
    await ProcessWithdrawalCancel(
        **operation_common.as_dict(),
        from_account=from_account,
        request_id=request_id,
    ).run()
