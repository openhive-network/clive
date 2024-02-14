from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import test_tools as tt

from clive_local_tools.cli import checkers
from clive_local_tools.data.constants import (
    WORKING_ACCOUNT,
    WORKING_ACCOUNT_HBD_LIQUID_BALANCE,
    WORKING_ACCOUNT_HIVE_LIQUID_BALANCE,
    WORKING_ACCOUNT_KEY_ALIAS,
)

if TYPE_CHECKING:
    from typer.testing import CliRunner

    from clive.__private.cli.clive_typer import CliveTyper

amount_to_deposit_hbd = tt.Asset.Hbd(0.238)
amount_to_deposit_hive = tt.Asset.Test(0.236)
large_amount = tt.Asset.Test(234234.236)
deposit_memo = "memo1"
withdrawal_memo = "memo2"


@pytest.mark.parametrize(
    ("amount_to_deposit", "working_account_balance"),
    [
        (amount_to_deposit_hive, WORKING_ACCOUNT_HIVE_LIQUID_BALANCE),
        (amount_to_deposit_hbd, WORKING_ACCOUNT_HBD_LIQUID_BALANCE),
    ],
    ids=["hive", "hbd"],
)
async def test_withdrawal_valid(
    cli_with_runner: tuple[CliveTyper, CliRunner],
    amount_to_deposit: tt.Asset.AnyT,
    working_account_balance: tt.Asset.AnyT,
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

    # ACT
    result = runner.invoke(
        cli,
        [
            "process",
            "savings",
            "withdrawal",
            f"--amount={amount_to_deposit.as_legacy()}",
            f"--password={WORKING_ACCOUNT.name}",
            f"--sign={WORKING_ACCOUNT_KEY_ALIAS}",
        ],
    )
    checkers.assert_no_exit_code_error(result)

    # ASSERT
    checkers.assert_balances(
        runner,
        cli,
        account_name=f"{WORKING_ACCOUNT.name}",
        asset_amount=tt.Asset.Hive(0),
        balance="Savings",
    )
    checkers.assert_balances(
        runner,
        cli,
        account_name=f"{WORKING_ACCOUNT.name}",
        asset_amount=working_account_balance - amount_to_deposit.amount,
        balance="Liquid",
    )


async def test_withdrawal_invalid(cli_with_runner: tuple[CliveTyper, CliRunner]) -> None:
    # ARRANGE
    cli, runner = cli_with_runner

    # ACT
    result = runner.invoke(
        cli,
        [
            "process",
            "savings",
            "withdrawal",
            f"--amount={large_amount.as_legacy()}",
            f"--password={WORKING_ACCOUNT.name}",
            f"--sign={WORKING_ACCOUNT_KEY_ALIAS}",
        ],
    )

    # ASSERT
    checkers.assert_exit_code(result, expected_code=1)
    checkers.assert_balances(
        runner,
        cli,
        account_name=f"{WORKING_ACCOUNT.name}",
        asset_amount=tt.Asset.Hive(0),
        balance="Savings",
    )
    checkers.assert_balances(
        runner,
        cli,
        account_name=f"{WORKING_ACCOUNT.name}",
        asset_amount=WORKING_ACCOUNT_HIVE_LIQUID_BALANCE,
        balance="Liquid",
    )


async def test_withdrawal_with_memo(cli_with_runner: tuple[CliveTyper, CliRunner]) -> None:
    # ARRANGE
    cli, runner = cli_with_runner

    result = runner.invoke(
        cli,
        [
            "process",
            "savings",
            "deposit",
            f"--amount={amount_to_deposit_hive.as_legacy()}",
            f"--memo={deposit_memo}",
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
            "withdrawal",
            f"--amount={amount_to_deposit_hive.as_legacy()}",
            f"--memo={withdrawal_memo}",
            f"--password={WORKING_ACCOUNT.name}",
            f"--sign={WORKING_ACCOUNT_KEY_ALIAS}",
        ],
    )
    checkers.assert_no_exit_code_error(result)

    # ASSERT
    checkers.assert_balances(
        runner,
        cli,
        account_name=f"{WORKING_ACCOUNT.name}",
        asset_amount=tt.Asset.Hive(0),
        balance="Savings",
    )
    checkers.assert_balances(
        runner,
        cli,
        account_name=f"{WORKING_ACCOUNT.name}",
        asset_amount=WORKING_ACCOUNT_HIVE_LIQUID_BALANCE - amount_to_deposit_hive.amount,
        balance="Liquid",
    )
    result = runner.invoke(cli, ["show", "pending", "withdrawals"])
    assert withdrawal_memo in result.output
    checkers.assert_no_exit_code_error(result)
