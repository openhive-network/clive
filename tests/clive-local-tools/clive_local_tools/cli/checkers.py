from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from click.testing import Result

from clive.__private.cli.exceptions import CLINoProfileUnlockedError
from clive.__private.core.formatters.humanize import humanize_bool

from .cli_tester import CLITester
from .exceptions import CLITestCommandError

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Literal

    import test_tools as tt

    from clive.__private.cli.types import AuthorityType
    from clive.__private.models.schemas import PublicKey


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
        asset_amount.token(testnet=False) in line and asset_amount.pretty_amount() in line and balance in line
        for line in output.split("\n")
    ), f"no {asset_amount.pretty_amount()} {asset_amount.token(testnet=False)}  in balances output:\n{output}"


def assert_pending_withrawals(context: CLITester | Result, account_name: str, asset_amount: tt.Asset.AnyT) -> None:
    result = context.show_pending_withdrawals() if isinstance(context, CLITester) else context
    output = result.output
    assert any(
        account_name in line and asset_amount.pretty_amount() in line and asset_amount.token(testnet=False) in line.upper()
        for line in output.split("\n")
    ), f"no {asset_amount.pretty_amount()} {asset_amount.token(testnet=False)} in pending withdrawals output:\n{output}"


def get_authority_output(context: CLITester | Result, authority: AuthorityType) -> str:
    result = context.show_authority(authority) if isinstance(context, CLITester) else context
    return result.output


def assert_is_authority(context: CLITester | Result, entry: str | PublicKey, authority: AuthorityType) -> None:
    output = get_authority_output(context, authority)
    table = output.split("\n")[2:]
    assert any(str(entry) in line for line in table), (
        f"no {entry} entry in show {authority}-authority output:\n{output}"
    )


def assert_is_not_authority(context: CLITester | Result, entry: str | PublicKey, authority: AuthorityType) -> None:
    output = get_authority_output(context, authority)
    table = output.split("\n")[2:]
    assert not any(str(entry) in line for line in table), (
        f"there is {entry} entry in show {authority}-authority output:\n{output}"
    )


def assert_authority_weight(
    context: CLITester | Result,
    entry: str | PublicKey,
    authority: AuthorityType,
    weight: int,
) -> None:
    output = get_authority_output(context, authority)
    assert any(str(entry) in line and f"{weight}" in line for line in output.split("\n")), (
        f"no {entry} entry with weight {weight} in show {authority}-authority output:\n{output}"
    )


def assert_weight_threshold(context: CLITester | Result, authority: AuthorityType, threshold: int) -> None:
    output = get_authority_output(context, authority)
    expected_output = f"weight threshold is {threshold}"
    command = f"show {authority}-authority"
    assert_output_contains(expected_output, output, command)


def assert_memo_key(context: CLITester | Result, memo_key: PublicKey) -> None:
    result = context.show_memo_key() if isinstance(context, CLITester) else context
    output = result.output
    expected_output = str(memo_key)
    command = "show memo-key"
    assert_output_contains(expected_output, output, command)


def assert_output_contains(expected_output: str, output: str, command: str | None = None) -> None:
    if command:
        assert expected_output in output, f"expected `{expected_output}` in command `{command}` output:\n{output}"
    else:
        assert expected_output in output, f"expected `{expected_output}` in output:\n{output}"


def assert_no_delegations(context: CLITester | Result) -> None:
    output = _get_output(context, CLITester.show_hive_power)
    expected_output = "no delegations"
    command = "show hive-power"
    assert_output_contains(expected_output, output, command)


def assert_withdraw_routes(context: CLITester | Result, to: str, percent: int, *, auto_vest: bool = False) -> None:
    output = _get_output(context, CLITester.show_hive_power)
    expected_output = str(percent)
    assert any(
        to in line and expected_output in line and humanize_bool(auto_vest) in line for line in output.split("\n")
    ), f"no withdraw route for `{to}` with percent `{expected_output}`"
    f" and `{auto_vest=}`in show hive-power output:\n{output}"


def assert_no_withdraw_routes(context: CLITester | Result) -> None:
    output = _get_output(context, CLITester.show_hive_power)
    expected_output = "no withdraw routes"
    command = "show hive-power"
    assert_output_contains(expected_output, output, command)


def assert_no_pending_power_down(context: CLITester | Result) -> None:
    output = _get_output(context, CLITester.show_pending_power_down)
    expected_output = "no pending power down"
    command = "show pending power-down"
    assert_output_contains(expected_output, output, command)


def assert_no_pending_power_ups(context: CLITester | Result) -> None:
    output = _get_output(context, CLITester.show_pending_power_ups)
    expected_output = "no pending power ups"
    command = "show pending power-ups"
    assert_output_contains(expected_output, output, command)


def assert_pending_removed_delegations(context: CLITester | Result, asset: tt.Asset.VestT) -> None:
    result = context.show_pending_removed_delegations() if isinstance(context, CLITester) else context
    output = result.output
    expected_output = asset.as_legacy()
    assert any(expected_output in line for line in output.split("\n")), (
        f"no entry for `{expected_output}` in show pending removed-delegations output:\n{output}"
    )


def assert_no_removed_delegations(context: CLITester | Result) -> None:
    output = _get_output(context, CLITester.show_pending_removed_delegations)
    expected_output = "no removed delegations"
    command = "show pending removed-delegations"
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


def assert_show_balances_title(context: CLITester | Result, account_name: str) -> None:
    output = _get_output(context, CLITester.show_balances)
    expected_output = f"Balances of `{account_name}` account"
    assert_output_contains(expected_output, output, "show balances")


def _get_output(context: CLITester | Result, function: Callable[[CLITester], Result] | None = None) -> str:
    if isinstance(context, CLITester):
        assert function, "`function` must be provided when `context` is `CLITester`"
        result = function(context)
    else:
        result = context
    return result.output


def assert_unlocked_profile(context: CLITester | Result, profile_name: str) -> None:
    output = _get_output(context, CLITester.show_profile)
    expected_output = f"Profile name: {profile_name}"
    assert_output_contains(expected_output, output, "show profile")


def assert_locked_profile(cli_tester: CLITester) -> None:
    with pytest.raises(CLITestCommandError, match=CLINoProfileUnlockedError.MESSAGE):
        cli_tester.show_profile()
