from __future__ import annotations

from json import JSONDecodeError, loads
from typing import TYPE_CHECKING

import pytest

from clive.__private.cli.commands.show.show_pending_change_recovery_account import (
    NO_PENDING_ACCOUNT_RECOVERY_MESSAGE,
    ShowPendingChangeRecoveryAccount,
)
from clive.__private.cli.commands.show.show_pending_decline_voting_rights import (
    NO_PENDING_DECLINE_VOTING_RIGHTS_MESSAGE,
    ShowPendingDeclineVotingRights,
)
from clive.__private.cli.exceptions import CLINoProfileUnlockedError
from clive.__private.core.formatters.humanize import humanize_bool
from clive.__private.models.transaction import Transaction
from clive_local_tools.data.constants import (
    DRY_RUN_MESSAGE,
    TRANSACTION_BROADCASTED_MESSAGE,
    TRANSACTION_CREATED_MESSAGE,
    TRANSACTION_LOADED_MESSAGE,
    TRANSACTION_SAVED_MESSAGE_PREFIX,
)

from .cli_tester import CLITester
from .exceptions import CLITestCommandError
from .result_wrapper import CLITestResult

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path
    from typing import Literal

    import test_tools as tt

    from clive.__private.core.types import AuthorityLevelRegular
    from clive.__private.models.schemas import PublicKey


def assert_balances(
    context: CLITester | CLITestResult,
    account_name: str,
    asset_amount: tt.Asset.AnyT,
    balance: Literal["Liquid", "Savings", "Unclaimed"],
) -> None:
    result = context.show_balances(account_name=account_name) if isinstance(context, CLITester) else context
    output = result.output
    assert account_name in output, f"no balances of {account_name} account in balances\n{result.info}"
    assert any(
        asset_amount.token() in line and asset_amount.pretty_amount() in line and balance in line
        for line in output.split("\n")
    ), f"no {asset_amount.pretty_amount()} {asset_amount.token()} in balances\n{result.info}"


def assert_pending_withrawals(
    context: CLITester | CLITestResult, account_name: str, asset_amount: tt.Asset.AnyT
) -> None:
    result = context.show_pending_withdrawals() if isinstance(context, CLITester) else context
    output = result.output
    assert any(
        account_name in line and asset_amount.pretty_amount() in line and asset_amount.token() in line.upper()
        for line in output.split("\n")
    ), f"no {asset_amount.pretty_amount()} {asset_amount.token()} in pending withdrawals\n{result.info}"


def get_authority_result(context: CLITester | CLITestResult, authority: AuthorityLevelRegular) -> CLITestResult:
    return context.show_authority(authority) if isinstance(context, CLITester) else context


def assert_is_authority(
    context: CLITester | CLITestResult, entry: str | PublicKey, authority: AuthorityLevelRegular
) -> None:
    result = get_authority_result(context, authority)
    table = result.output.split("\n")[2:]
    assert any(str(entry) in line for line in table), f"no {entry} entry in show {authority}-authority\n{result.info}"


def assert_is_not_authority(
    context: CLITester | CLITestResult, entry: str | PublicKey, authority: AuthorityLevelRegular
) -> None:
    result = get_authority_result(context, authority)
    table = result.output.split("\n")[2:]
    assert not any(str(entry) in line for line in table), (
        f"there is {entry} entry in show {authority}-authority\n{result.info}"
    )


def assert_authority_weight(
    context: CLITester | CLITestResult,
    entry: str | PublicKey,
    authority: AuthorityLevelRegular,
    weight: int,
) -> None:
    result = get_authority_result(context, authority)
    output = result.output
    assert any(str(entry) in line and f"{weight}" in line for line in output.split("\n")), (
        f"no {entry} entry with weight {weight} in show {authority}-authority\n{result.info}"
    )


def assert_weight_threshold(
    context: CLITester | CLITestResult, authority: AuthorityLevelRegular, threshold: int
) -> None:
    result = get_authority_result(context, authority)
    expected_output = f"weight threshold is {threshold}"
    assert_output_contains(expected_output, result)


def assert_memo_key(context: CLITester | CLITestResult, memo_key: PublicKey) -> None:
    result = context.show_memo_key() if isinstance(context, CLITester) else context
    expected_output = str(memo_key)
    assert_output_contains(expected_output, result)


def assert_output_contains(expected_output: str, context: CLITestResult | str) -> None:
    if isinstance(context, CLITestResult):
        result = context
        output = result.output
        assert expected_output in output, f"expected `{expected_output}` in output, result info\n{result.info}"
    else:
        output = context
        assert expected_output in output, f"expected `{expected_output}` in output:\n{output}"


def assert_output_does_not_contain(part: str, output: str) -> None:
    assert part not in output, f"Unexpected occurrence of `{part}` in output:\n{output}"


def assert_no_delegations(context: CLITester | CLITestResult) -> None:
    result = _get_result(context, lambda cli_tester: cli_tester.show_hive_power())
    expected_output = "no delegations"
    assert_output_contains(expected_output, result)


def assert_withdraw_routes(
    context: CLITester | CLITestResult, to: str, percent: int, *, auto_vest: bool = False
) -> None:
    result = _get_result(context, lambda cli_tester: cli_tester.show_hive_power())
    output = result.output
    expected_output = str(percent)
    assert any(
        to in line and expected_output in line and humanize_bool(auto_vest) in line for line in output.split("\n")
    ), f"no withdraw route for `{to}` with percent `{expected_output}`"
    f" and `{auto_vest=}`in show hive-power\n{result.info}"


def assert_no_withdraw_routes(context: CLITester | CLITestResult) -> None:
    result = _get_result(context, lambda cli_tester: cli_tester.show_hive_power())
    expected_output = "no withdraw routes"
    assert_output_contains(expected_output, result)


def assert_no_pending_power_down(context: CLITester | CLITestResult) -> None:
    result = _get_result(context, lambda cli_tester: cli_tester.show_pending_power_down())
    expected_output = "no pending power down"
    assert_output_contains(expected_output, result)


def assert_no_pending_power_ups(context: CLITester | CLITestResult) -> None:
    result = _get_result(context, lambda cli_tester: cli_tester.show_pending_power_ups())
    expected_output = "no pending power ups"
    assert_output_contains(expected_output, result)


def assert_pending_removed_delegations(context: CLITester | CLITestResult, asset: tt.Asset.VestT) -> None:
    result = context.show_pending_removed_delegations() if isinstance(context, CLITester) else context
    output = result.output
    expected_output = asset.as_legacy()
    assert any(expected_output in line for line in output.split("\n")), (
        f"no entry for `{expected_output}` in pending delegations\n{result.info}"
    )


def assert_no_removed_delegations(context: CLITester | CLITestResult) -> None:
    result = _get_result(context, lambda cli_tester: cli_tester.show_pending_removed_delegations())
    expected_output = "no removed delegations"
    assert_output_contains(expected_output, result)


def assert_pending_change_recovery_account(
    context: CLITester | CLITestResult, account_to_recover: str, new_recovery_account_name: str
) -> None:
    result = _get_result(context, lambda cli_tester: cli_tester.show_pending_change_recovery_account())
    assert_output_contains(ShowPendingChangeRecoveryAccount._format_table_title(account_to_recover), result)
    assert_output_contains(new_recovery_account_name, result)


def assert_no_pending_change_recovery_account(context: CLITester | CLITestResult) -> None:
    result = _get_result(context, lambda cli_tester: cli_tester.show_pending_change_recovery_account())
    expected_output = NO_PENDING_ACCOUNT_RECOVERY_MESSAGE
    assert_output_contains(expected_output, result)


def assert_pending_decline_voting_rights(context: CLITester | CLITestResult, account: str) -> None:
    result = _get_result(context, lambda cli_tester: cli_tester.show_pending_decline_voting_rights())
    assert_output_contains(ShowPendingDeclineVotingRights._format_table_title(account), result)
    assert_output_contains(account, result)


def assert_no_pending_decline_voting_rights(context: CLITester | CLITestResult) -> None:
    result = _get_result(context, lambda cli_tester: cli_tester.show_pending_decline_voting_rights())
    expected_output = NO_PENDING_DECLINE_VOTING_RIGHTS_MESSAGE
    assert_output_contains(expected_output, result)


def assert_exit_code(
    context: CLITestResult | pytest.ExceptionInfo[CLITestCommandError] | int, expected_exit_code: int
) -> None:
    if isinstance(context, CLITestResult):
        result = context
        actual_exit_code = result.exit_code
        message = f"Exit code '{actual_exit_code}' is different than expected '{expected_exit_code}'.\n{result.info}"
    elif isinstance(context, pytest.ExceptionInfo):
        result = context.value.result
        actual_exit_code = result.exit_code
        message = f"Exit code '{actual_exit_code}' is different than expected '{expected_exit_code}'.\n{result.info}"
    else:
        actual_exit_code = context
        message = f"Exit code '{actual_exit_code}' is different than expected '{expected_exit_code}'."

    assert actual_exit_code == expected_exit_code, message


def assert_show_balances_title(context: CLITester | CLITestResult, account_name: str) -> None:
    result = _get_result(context, lambda cli_tester: cli_tester.show_balances())
    expected_output = f"Balances of `{account_name}` account"
    assert_output_contains(expected_output, result)


def _get_result(
    context: CLITester | CLITestResult, function: Callable[[CLITester], CLITestResult] | None = None
) -> CLITestResult:
    if isinstance(context, CLITester):
        assert function, "`function` must be provided when `context` is `CLITester`"
        result = function(context)
    else:
        result = context
    return result


def assert_unlocked_profile(context: CLITester | CLITestResult, profile_name: str) -> None:
    result = _get_result(context, lambda cli_tester: cli_tester.show_profile())
    expected_output = f"Profile name: {profile_name}"
    assert_output_contains(expected_output, result)


def assert_locked_profile(cli_tester: CLITester) -> None:
    with pytest.raises(CLITestCommandError, match=CLINoProfileUnlockedError.MESSAGE):
        cli_tester.show_profile()


def assert_transaction_file_is_signed(file_path: Path, *, signatures_count: int | None = None) -> None:
    transaction = Transaction.parse_file(file_path)
    assert signatures_count is None or signatures_count >= 1, (
        "signatures_count must be None or greater than or equal to 1"
    )

    if signatures_count is None:
        assert transaction.signatures, "Transaction should be signed."
        return

    count = len(transaction.signatures)
    assert count == signatures_count, f"Transaction should be signed {signatures_count} times."


def assert_transaction_file_is_unsigned(file_path: Path) -> None:
    transaction = Transaction.parse_file(file_path)
    assert len(transaction.signatures) == 0, "Transaction should be unsigned."


def assert_contains_dry_run_message(message: str) -> None:
    assert_output_contains(DRY_RUN_MESSAGE, message)


def assert_contains_transaction_created_message(message: str) -> None:
    """This message is shown when transaction has been created, but not broadcasted and not loaded from a file."""
    assert_output_contains(TRANSACTION_CREATED_MESSAGE, message)


def assert_contains_transaction_broadcasted_message(message: str) -> None:
    """This message is shown when transaction was broadcasted."""
    assert_output_contains(TRANSACTION_BROADCASTED_MESSAGE, message)


def assert_does_not_contain_transaction_broadcasted_message(message: str) -> None:
    """This message is shown when transaction was broadcasted."""
    assert_output_does_not_contain(TRANSACTION_BROADCASTED_MESSAGE, message)


def assert_contains_transaction_loaded_message(message: str) -> None:
    """This message is shown when transaction was loaded from file, but not broadcasted."""
    assert_output_contains(TRANSACTION_LOADED_MESSAGE, message)


def assert_contains_transaction_saved_to_file_message(file_path: str | Path, message: str) -> None:
    """This message is shown when transaction was saved to file."""
    prefix = TRANSACTION_SAVED_MESSAGE_PREFIX
    # First ensure that the expected prefix is in the message
    assert_output_contains(prefix, message)

    # Then ensure that the file path is in the message
    _, _, rest = message.partition(prefix)
    normalized = rest.replace("\n", "")

    assert str(file_path) in normalized, f"Transaction was saved but looks like to a wrong file: {normalized}"


def assert_result_contains_valid_json(result: CLITestResult) -> None:
    """Asserts that the provided content is valid JSON."""
    try:
        loads(result.output)
    except JSONDecodeError:
        pytest.fail(f"Expected valid JSON content.\n{result.info}")
