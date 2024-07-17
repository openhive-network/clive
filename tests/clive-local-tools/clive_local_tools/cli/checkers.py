from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import pytest
import test_tools as tt
from click.testing import Result

from clive.__private.core.formatters.humanize import humanize_bool

from .cli_tester import CLITester

if TYPE_CHECKING:
    from typing import Literal

    from clive.__private.cli.types import AuthorityType
    from clive_local_tools.cli.get_data_from_table import (
        TableDataType,
        TableRowType,
    )
    from schemas.fields.basic import PublicKey

    from .exceptions import CLITestCommandError


from clive.__private.cli.commands.show.show_transfer_schedule import (
    DEFAULT_UPCOMING_FUTURE_SCHEDULED_TRANSFERS_AMOUNT,
)
from clive.__private.core.shorthand_timedelta import shorthand_timedelta_to_timedelta


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
    command = f"show {authority}-authority"
    assert_output_contains(expected_output, output, command)


def assert_memo_key(context: CLITester | Result, memo_key: PublicKey) -> None:
    result = context.show_memo_key() if isinstance(context, CLITester) else context
    output = result.output
    expected_output = str(memo_key)
    command = "show memo-key"
    assert_output_contains(expected_output, output, command)


def assert_output_contains(expected_output: str, output: str, command: str) -> None:
    assert expected_output in output, f"expected `{expected_output}` in command `{command}` output:\n{output}"


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
    assert any(
        expected_output in line for line in output.split("\n")
    ), f"no entry for `{expected_output}` in show pending removed-delegations output:\n{output}"


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


def _get_output(context: CLITester | Result, function: Callable[[CLITester], Result] | None = None) -> str:
    if isinstance(context, CLITester):
        assert function, "`function` must be provided when `context` is `CLITester`"
        result = function(context)
    else:
        result = context
    return result.output


def assert_transaction_in_blockchain(node: tt.RawNode, transaction_id: str) -> None:
    node.wait_number_of_blocks(1)
    node.api.account_history.get_transaction(
        id_=transaction_id,
        include_reversible=True,
    )


def assert_transfers_existing_number(
    table: TableDataType,
    required_number: int,
    *,
    upcoming: bool,
) -> None:
    if upcoming:
        message = f"There should be {required_number} of upcoming scheduled transfers."
    else:
        message = f"There should be {required_number} of scheduled transfers."
    assert len(table) == required_number, message


def assert_max_number_of_upcoming(table: TableDataType) -> None:
    assert (
        len(table) == DEFAULT_UPCOMING_FUTURE_SCHEDULED_TRANSFERS_AMOUNT
    ), f"Max number of incoming transfers should be {DEFAULT_UPCOMING_FUTURE_SCHEDULED_TRANSFERS_AMOUNT}."


def assert_no_scheduled_transfers_for_account(result_output: str, account_name: str) -> None:
    assert (
        f"Account `{account_name}` has no scheduled transfers." in result_output
    ), "There should be no scheduled transfers."


def assert_from_account(scheduled_transfer: TableRowType, account_name: str) -> None:
    assert "From" in scheduled_transfer, "There should be 'From' key for scheduled_transfer."
    assert scheduled_transfer["From"] == account_name, f"Created scheduled transfer should be from `{account_name}`"


def assert_coverage_scheduled_transfer(  # noqa: PLR0913
    scheduled_transfer: TableRowType,
    _from: str,
    to: str,
    pair_id: int,
    amount: tt.Asset.HbdT | tt.Asset.HiveT,
    memo: str,
    frequency: str,
    remaining: int,
) -> None:
    def __assert_coverage_scheduled_transfer_keys(scheduled_transfer: TableRowType) -> None:
        keys = ["From", "To", "Pair id", "Amount", "Memo", "Next", "Frequency", "Remaining", "Failures"]
        for key in keys:
            assert key in scheduled_transfer, f"Field `{key}` should be defined."

    __assert_coverage_scheduled_transfer_keys(scheduled_transfer)
    assert scheduled_transfer["From"] == _from, "Value for `From` should match."
    assert scheduled_transfer["To"] == to, "Value for `To` should match."
    assert int(scheduled_transfer["Pair id"]) == pair_id, "Value for `Pair id` should match."
    assert scheduled_transfer["Amount"] == amount.as_legacy(), "Value for `Amount` should match."
    assert scheduled_transfer["Memo"] == memo, "Value for `Memo` should match."
    assert shorthand_timedelta_to_timedelta(scheduled_transfer["Frequency"]) == shorthand_timedelta_to_timedelta(
        frequency
    ), "Value for `Frequency` should match."
    assert int(scheduled_transfer["Remaining"]) == remaining, "Value for `Remaining` should match."


def assert_coverage_upcoming_scheduled_transfer(  # noqa: PLR0913
    upcoming_scheduled_transfer: TableRowType,
    _from: str,
    to: str,
    pair_id: int,
    amount: tt.Asset.HbdT | tt.Asset.HiveT,
    possible_amount_after_operation: tt.Asset.HbdT | tt.Asset.HiveT,
    frequency: str,
) -> None:
    def __assert_coverage_upcoming_scheduled_transfer_keys(upcoming_scheduled_transfer: TableRowType) -> None:
        keys = ["From", "To", "Pair id", "Amount", "Possible balance after operation", "Next", "Frequency"]
        for key in keys:
            assert key in upcoming_scheduled_transfer, f"Field `{key}` should be defined."

    __assert_coverage_upcoming_scheduled_transfer_keys(upcoming_scheduled_transfer)
    assert upcoming_scheduled_transfer["From"] == _from, "Value for `From` should match."
    assert upcoming_scheduled_transfer["To"] == to, "Value for `To` should match."
    assert int(upcoming_scheduled_transfer["Pair id"]) == pair_id, "Value for `Pair id` should match."
    assert upcoming_scheduled_transfer["Amount"] == amount.as_legacy(), "Value for `Amount` should match."
    assert (
        upcoming_scheduled_transfer["Possible balance after operation"] == possible_amount_after_operation.as_legacy()
    ), "Value for `Possible balance after operation` should match."
    assert_scheduled_transfers_frequency_value(upcoming_scheduled_transfer, frequency)


def assert_calculated_possible_balance(
    possible_balance: str | tt.Asset.HiveT | tt.Asset.HbdT,
    upcoming_scheduled_transfer: TableRowType,
) -> None:
    message = "Values of `possible balance after operation` should match."
    if isinstance(possible_balance, (tt.Asset.HbdT, tt.Asset.HiveT)):
        assert upcoming_scheduled_transfer["Possible balance after operation"] == possible_balance.as_legacy(), message
    else:
        assert upcoming_scheduled_transfer["Possible balance after operation"] == possible_balance, message


def assert_scheduled_transfers_frequency_value(scheduled_transfer: TableRowType, frequency: str) -> None:
    assert shorthand_timedelta_to_timedelta(scheduled_transfer["Frequency"]) == shorthand_timedelta_to_timedelta(
        frequency
    ), "Value for `Frequency should match"
