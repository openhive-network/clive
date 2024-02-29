from __future__ import annotations

from typing import TYPE_CHECKING

from .show import balances as show_balances

if TYPE_CHECKING:
    from typing import Literal

    import test_tools as tt

    from clive.__private.cli.types import AuthorityType
    from clive_local_tools.cli.testing_cli import TestingCli
    from schemas.fields.basic import PublicKey


def assert_balances(
    testing_cli: TestingCli,
    account_name: str,
    asset_amount: tt.Asset.AnyT,
    balance: Literal["Liquid", "Savings", "Unclaimed"],
) -> None:
    result = show_balances(testing_cli, account_name=account_name)
    output = result.output
    assert account_name in output, f"no balances of {account_name} account in balances output: {output}"
    assert any(
        asset_amount.token() in line and asset_amount.pretty_amount() in line and balance in line
        for line in output.split("\n")
    ), f"no {asset_amount.pretty_amount()} {asset_amount.token()}  in balances output:\n{output}"


def assert_pending_withrawals(testing_cli: TestingCli, account_name: str, asset_amount: tt.Asset.AnyT) -> None:
    result = testing_cli.show_pending_withdrawals()
    output = result.output
    assert any(
        account_name in line and asset_amount.pretty_amount() in line and asset_amount.token() in line.upper()
        for line in output.split("\n")
    ), f"no {asset_amount.pretty_amount()} {asset_amount.token()} in pending withdrawals output:\n{output}"


def assert_is_authority(
    testing_cli: TestingCli,
    entry: str | PublicKey,
    authority: AuthorityType,
) -> None:
    result = testing_cli.show_authority(authority)
    output = result.output
    table = output.split("\n")[2:]
    assert any(
        str(entry) in line for line in table
    ), f"no {entry} entry in show {authority}-authority output:\n{output}"


def assert_is_not_authority(
    testing_cli: TestingCli,
    entry: str | PublicKey,
    authority: AuthorityType,
) -> None:
    result = testing_cli.show_authority(authority)
    output = result.output
    table = output.split("\n")[2:]
    assert not any(
        str(entry) in line for line in table
    ), f"there is {entry} entry in show {authority}-authority output:\n{output}"


def assert_authority_weight(
    testing_cli: TestingCli,
    entry: str | PublicKey,
    authority: AuthorityType,
    weight: int,
) -> None:
    result = testing_cli.show_authority(authority)
    output = result.output
    assert any(
        str(entry) in line and f"{weight}" in line for line in output.split("\n")
    ), f"no {entry} entry with weight {weight} in show {authority}-authority output:\n{output}"


def assert_weight_threshold(
    testing_cli: TestingCli,
    authority: AuthorityType,
    threshold: int,
) -> None:
    result = testing_cli.show_authority(authority)
    output = result.output
    assert f"weight threshold is {threshold}" in output


def assert_memo_key(
    testing_cli: TestingCli,
    memo_key: PublicKey,
) -> None:
    result = testing_cli.show_memo_key()
    output = result.output
    assert str(memo_key) in output
