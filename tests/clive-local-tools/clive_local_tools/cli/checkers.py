from __future__ import annotations

from itertools import pairwise
from typing import TYPE_CHECKING, Callable

import pytest
from click.testing import Result

from clive.__private.core.formatters.humanize import humanize_bool

from .cli_tester import CLITester

if TYPE_CHECKING:
    from typing import Literal

    import test_tools as tt

    from clive.__private.cli.types import AuthorityType
    from schemas.fields.basic import PublicKey

    from .exceptions import CLITestCommandError


def assert_balances(
    context: CLITester | Result,
    account_name: str,
    asset_amount: tt.Asset.AnyT,
    balance: Literal["Liquid", "Savings", "Unclaimed"],
) -> None:
    result = context.show_balances(account_name=account_name) if isinstance(context, CLITester) else context
    output = result.output
    assert account_name in output, f"no balances of {account_name} account in balances output: {output}"
    assert any(
        asset_amount.token() in line and asset_amount.pretty_amount() in line and balance in line
        for line in output.split("\n")
    ), f"no {asset_amount.pretty_amount()} {asset_amount.token()}  in balances output:\n{output}"


def assert_pending_withrawals(context: CLITester | Result, account_name: str, asset_amount: tt.Asset.AnyT) -> None:
    result = context.show_pending_withdrawals() if isinstance(context, CLITester) else context
    output = result.output
    assert any(
        account_name in line and asset_amount.pretty_amount() in line and asset_amount.token() in line.upper()
        for line in output.split("\n")
    ), f"no {asset_amount.pretty_amount()} {asset_amount.token()} in pending withdrawals output:\n{output}"


def get_authority_output(context: CLITester | Result, authority: AuthorityType) -> str:
    result = context.show_authority(authority) if isinstance(context, CLITester) else context
    return result.output


def assert_is_authority(context: CLITester | Result, entry: str | PublicKey, authority: AuthorityType) -> None:
    output = get_authority_output(context, authority)
    table = output.split("\n")[2:]
    assert any(
        str(entry) in line for line in table
    ), f"no {entry} entry in show {authority}-authority output:\n{output}"


def assert_is_not_authority(context: CLITester | Result, entry: str | PublicKey, authority: AuthorityType) -> None:
    output = get_authority_output(context, authority)
    table = output.split("\n")[2:]
    assert not any(
        str(entry) in line for line in table
    ), f"there is {entry} entry in show {authority}-authority output:\n{output}"


def assert_authority_weight(
    context: CLITester | Result,
    entry: str | PublicKey,
    authority: AuthorityType,
    weight: int,
) -> None:
    output = get_authority_output(context, authority)
    assert any(
        str(entry) in line and f"{weight}" in line for line in output.split("\n")
    ), f"no {entry} entry with weight {weight} in show {authority}-authority output:\n{output}"


def assert_weight_threshold(context: CLITester | Result, authority: AuthorityType, threshold: int) -> None:
    output = get_authority_output(context, authority)
    expected_output = f"weight threshold is {threshold}"
    command=f"show {authority}-authority"
    assert_output_contains(expected_output, output, command)


def assert_memo_key(context: CLITester | Result, memo_key: PublicKey) -> None:
    result = context.show_memo_key() if isinstance(context, CLITester) else context
    output = result.output
    expected_output = str(memo_key)
    command=f"show memo-key"
    assert_output_contains(expected_output, output, command)


def get_output(context: CLITester | Result, function: Callable[[CLITester], Result]) -> str:
    result = function(context) if isinstance(context, CLITester) else context
    return result.output


def assert_output_contains(expected_output: str, output: str, command: str) -> None:
    assert expected_output in output, f"expected `{expected_output}` in command `{command}` output:\n{output}"


def assert_effective_voting_power(context: CLITester | Result, asset: str) -> None:
    output = get_output(context, CLITester.show_hive_power)
    hive_power_type = "Effective"
    """contains"""
    assert any(
        hive_power_type in line and asset in line for line in output.split("\n")
    ), f"no entry for `{hive_power_type}` voting power with amount `{asset}` in show hive-power output:\n{output}"


def assert_power_down(context: CLITester | Result, asset: str) -> None:
    output = get_output(context, CLITester.show_hive_power)
    """contains"""
    assert any(
        asset in line for line in output.split("\n")
    ), f"no entry for `{asset}` in show pending power-downs output:\n{output}"


def assert_delegations(context: CLITester | Result, delegatee: str, asset: str) -> None:
    output = get_output(context, CLITester.show_hive_power)
    is_delegation = False
    lines = output.split("\n")
    """contains"""
    for this_line, next_line in pairwise(lines):
        if delegatee in this_line and (asset in this_line or asset in next_line):
            is_delegation = True
            break
    assert is_delegation, f"no delegation for `{delegatee}` with asset `{asset}` in show hive-power output:\n{output}"


def assert_no_delegations(context: CLITester | Result) -> None:
    output = get_output(context, CLITester.show_hive_power)
    expected_output = "no delegations"
    command=f"show hive-power"
    assert_output_contains(expected_output, output, command)


def assert_withdraw_routes(context: CLITester | Result, to: str, percent: int, *, auto_vest: bool = False) -> None:
    output = get_output(context, CLITester.show_hive_power)
    expected_output = str(percent)
    assert any(
        to in line and expected_output in line and humanize_bool(auto_vest) in line for line in output.split("\n")
    ), f"no withdraw route for `{to}` with percent `{expected_output}`"
    f" and `{auto_vest=}`in show hive-power output:\n{output}"


def assert_no_withdraw_routes(context: CLITester | Result) -> None:
    output = get_output(context, CLITester.show_hive_power)
    expected_output = "no withdraw routes"
    command=f"show hive-power"
    assert_output_contains(expected_output, output, command)


def assert_pending_power_down(context: CLITester | Result, asset: str) -> None:
    result = context.show_pending_power_down() if isinstance(context, CLITester) else context
    output = result.output
    """contains"""
    assert any(
        asset in line for line in output.split("\n")
    ), f"no entry for `{asset}` in show pending power-downs output:\n{output}"


def assert_no_pending_power_down(context: CLITester | Result) -> None:
    output = get_output(context, CLITester.show_pending_power_down)
    expected_output = "no pending power down"
    command=f"show pending power-down"
    assert_output_contains(expected_output, output, command)


def assert_pending_power_ups(context: CLITester | Result, asset: str) -> None:
    result = context.show_pending_power_ups() if isinstance(context, CLITester) else context
    output = result.output
    """contains"""
    assert any(
        asset in line for line in output.split("\n")
    ), f"no entry for `{asset}` in show pending power-ups output:\n{output}"


def assert_no_pending_power_ups(context: CLITester | Result) -> None:
    output = get_output(context, CLITester.show_pending_power_ups)
    expected_output = "no pending power ups"
    command=f"show pending power-ups"
    assert_output_contains(expected_output, output, command)


def assert_pending_removed_delegations(context: CLITester | Result, asset: tt.Asset.VestT) -> None:
    result = context.show_pending_removed_delegations() if isinstance(context, CLITester) else context
    output = result.output
    expected_output = asset.as_legacy()
    assert any(
        expected_output in line for line in output.split("\n")
    ), f"no entry for `{expected_output}` in show pending removed-delegations output:\n{output}"


def assert_no_removed_delegations(context: CLITester | Result) -> None:
    output = get_output(context, CLITester.show_pending_removed_delegations)
    expected_output = "no removed delegations"
    command=f"show pending removed-delegations"
    assert_output_contains(expected_output, output, command)


def assert_no_exit_code_error(result: Result | pytest.ExceptionInfo[CLITestCommandError] | int) -> None:
    assert_exit_code(result, 0)


def assert_exit_code(result: Result | pytest.ExceptionInfo[CLITestCommandError] | int, expected_exit_code: int) -> None:
    if isinstance(result, Result):
        actual_exit_code = result.exit_code
        message = (
            f"Exit code '{actual_exit_code}' is different than expected '{expected_exit_code}'.\n"
            f"Output:\n{result.output}"
        )
    elif isinstance(result, pytest.ExceptionInfo):
        command_result = result.value.result
        actual_exit_code = command_result.exit_code
        message = (
            f"Exit code '{actual_exit_code}' is different than expected '{expected_exit_code}'.\n"
            f"Output:\n{command_result.output}"
        )
    else:
        actual_exit_code = result
        message = f"Exit code '{actual_exit_code}' is different than expected '{expected_exit_code}'."

    assert actual_exit_code == expected_exit_code, message


def assert_transaction_in_blockchain(node: tt.RawNode, transaction_id: str) -> None:
    node.wait_number_of_blocks(1)
    node.api.account_history.get_transaction(
        id_=transaction_id,
        include_reversible=True,
    )
