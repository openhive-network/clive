from __future__ import annotations

from typing import TYPE_CHECKING

import test_tools as tt

from clive_local_tools.cli import checkers
from clive_local_tools.data.constants import WORKING_ACCOUNT, WORKING_ACCOUNT_KEY_ALIAS

if TYPE_CHECKING:
    from typer.testing import CliRunner

    from clive.__private.cli.clive_typer import CliveTyper

amount_to_deposit = tt.Asset.Test(0.234)


async def test_withdrawal_cancel_valid(cli_with_runner: tuple[CliveTyper, CliRunner]) -> None:
    # ARRANGE
    cli, runner = cli_with_runner

    request_id = 13

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
            f"--request-id={request_id}",
            f"--amount={amount_to_deposit.as_legacy()}",
            f"--password={WORKING_ACCOUNT.name}",
            f"--sign={WORKING_ACCOUNT_KEY_ALIAS}",
        ],
    )
    checkers.assert_no_exit_code_error(result)

    # ACT
    result = runner.invoke(
        cli,
        [
            "process",
            "savings",
            "withdrawal-cancel",
            f"--request-id={request_id}",
            f"--password={WORKING_ACCOUNT.name}",
            f"--sign={WORKING_ACCOUNT_KEY_ALIAS}",
        ],
    )
    checkers.assert_no_exit_code_error(result)

    # ASSERT
    result = runner.invoke(cli, ["show", "pending", "withdrawals"])
    checkers.assert_no_exit_code_error(result)
    assert str(amount_to_deposit.amount) not in result.stdout


async def test_withdrawal_cancel_invalid(cli_with_runner: tuple[CliveTyper, CliRunner]) -> None:
    # ARRANGE
    cli, runner = cli_with_runner
    actual_request_id = 23
    invalid_request_id = 24

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
            f"--request-id={actual_request_id}",
            f"--amount={amount_to_deposit.as_legacy()}",
            f"--password={WORKING_ACCOUNT.name}",
            f"--sign={WORKING_ACCOUNT_KEY_ALIAS}",
        ],
    )
    checkers.assert_no_exit_code_error(result)

    # ACT
    result = runner.invoke(
        cli,
        [
            "process",
            "savings",
            "withdrawal-cancel",
            f"--request-id={invalid_request_id}",
            f"--password={WORKING_ACCOUNT.name}",
            f"--sign={WORKING_ACCOUNT_KEY_ALIAS}",
        ],
    )
    checkers.assert_exit_code(result, expected_code=1)

    # ASSERT
    result = runner.invoke(cli, ["show", "pending", "withdrawals"])
    checkers.assert_no_exit_code_error(result)
    checkers.assert_pending_withrawals(
        result.stdout,
        account_name=f"{WORKING_ACCOUNT.name}",
        asset_amount=amount_to_deposit,
    )
