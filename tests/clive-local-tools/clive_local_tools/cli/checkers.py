from __future__ import annotations

from typing import TYPE_CHECKING

from .show import balances as show_balances

if TYPE_CHECKING:
    from typing import Literal

    import test_tools as tt
    from click.testing import Result
    from typer.testing import CliRunner

    from clive.__private.cli.clive_typer import CliveTyper


def assert_no_exit_code_error(result: Result) -> None:
    exit_code = 0
    message = f"Exit code '{result.exit_code}' is different than expected '{exit_code}'. Output:\n{result.output}"
    assert result.exit_code == exit_code, message


def assert_exit_code(result: Result, expected_code: int) -> None:
    message = f"Exit code '{result.exit_code}' is different than expected '{expected_code}'. Output:\n{result.output}"
    assert result.exit_code == expected_code, message


def assert_balances(
    runner: CliRunner,
    cli: CliveTyper,
    account_name: str,
    asset_amount: tt.Asset.AnyT,
    balance: Literal["Liquid", "Savings", "Unclaimed"],
) -> None:
    result = show_balances(runner, cli, account_name=account_name)
    output = result.output

    assert_no_exit_code_error(result)
    assert account_name in output, f"no balances of {account_name} account in balances output: {output}"
    assert any(
        asset_amount.token() in line and asset_amount.pretty_amount() in line and balance in line
        for line in output.split("\n")
    ), f"no {asset_amount.pretty_amount()} {asset_amount.token()}  in balances output:\n{output}"


def assert_pending_withrawals(output: str, *, account_name: str, asset_amount: tt.Asset.AnyT) -> None:
    assert any(
        account_name in line and asset_amount.pretty_amount() in line and asset_amount.token() in line.upper()
        for line in output.split("\n")
    ), f"no {asset_amount.pretty_amount()} {asset_amount.token()} in pending withdrawals output:\n{output}"
