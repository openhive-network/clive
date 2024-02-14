from __future__ import annotations

from typing import TYPE_CHECKING

import test_tools as tt

from clive_local_tools.cli import checkers
from clive_local_tools.data.constants import WORKING_ACCOUNT, WORKING_ACCOUNT_KEY_ALIAS

if TYPE_CHECKING:
    from typer.testing import CliRunner

    from clive.__private.cli.clive_typer import CliveTyper

amount_to_withdraw = tt.Asset.Test(0.111)
amount_to_withdraw2 = tt.Asset.Test(0.112)
amount_to_deposit = tt.Asset.Test(0.345)


async def test_show_pending_withdrawals_none(
    cli_with_runner: tuple[CliveTyper, CliRunner],
) -> None:
    # ARRANGE
    cli, runner = cli_with_runner

    # ACT
    result = runner.invoke(cli, ["show", "pending", "withdrawals"])

    # ASSERT
    checkers.assert_no_exit_code_error(result)
    assert "no pending withdrawals" in result.stdout


async def test_show_pending_withdrawals_basic(
    cli_with_runner: tuple[CliveTyper, CliRunner],
) -> None:
    # ARRANGE
    cli, runner = cli_with_runner

    result = runner.invoke(
        cli,
        [
            "process",
            "savings",
            "deposit",
            f"--amount={amount_to_deposit.as_legacy()}",
            f"--password={WORKING_ACCOUNT.name}",
            f"--sign={WORKING_ACCOUNT_KEY_ALIAS}",
        ],
    )
    checkers.assert_no_exit_code_error(result)

    result = runner.invoke(
        cli,
        [
            "process",
            "savings",
            "withdrawal",
            f"--amount={amount_to_withdraw.as_legacy()}",
            f"--password={WORKING_ACCOUNT.name}",
            f"--sign={WORKING_ACCOUNT_KEY_ALIAS}",
        ],
    )
    checkers.assert_no_exit_code_error(result)
    result = runner.invoke(
        cli,
        [
            "process",
            "savings",
            "withdrawal",
            f"--amount={amount_to_withdraw2.as_legacy()}",
            f"--password={WORKING_ACCOUNT.name}",
            f"--sign={WORKING_ACCOUNT_KEY_ALIAS}",
        ],
    )
    checkers.assert_no_exit_code_error(result)

    # ACT
    result = runner.invoke(cli, ["show", "pending", "withdrawals"])

    # ASSERT
    checkers.assert_no_exit_code_error(result)
    checkers.assert_pending_withrawals(
        result.stdout,
        account_name=f"{WORKING_ACCOUNT.name}",
        asset_amount=amount_to_withdraw,
    )
    checkers.assert_pending_withrawals(
        result.stdout,
        account_name=f"{WORKING_ACCOUNT.name}",
        asset_amount=amount_to_withdraw2,
    )
