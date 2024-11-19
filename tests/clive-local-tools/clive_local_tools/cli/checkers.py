from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Iterable

import pytest
from click.testing import Result

from clive.__private.core.formatters.humanize import humanize_bool
from clive.__private.core.profile import Profile

from .cli_tester import CLITester

if TYPE_CHECKING:
    from typing import Literal

    import test_tools as tt

    from clive.__private.cli.types import AuthorityType
    from clive.__private.models.schemas import PublicKey

    from .exceptions import CLITestCommandError


class IsNotSet:
    """A class to represent a value that is not set."""


class ProfileAccountsChecker:
    def __init__(self, profile_name: str) -> None:
        self.profile_name = profile_name

    @property
    def profile(self) -> Profile:
        return Profile.load(name=self.profile_name)

    def assert_working_account(self, working_account: str | IsNotSet | None = None) -> None:
        """
        Check working account of profile.

        Args:
        working_account: The name of the working account to check. For:
        * IsNotSet - check if the working account is not set,
        * None - skip the check.
        """
        if working_account is not None:
            profile = self.profile
            is_working_account_set = profile.accounts.has_working_account

            if isinstance(working_account, IsNotSet):
                assert not is_working_account_set, "Working account is set while should not be."
            else:
                assert is_working_account_set, f"Working account is not set while should be {working_account}."
                assert working_account == profile.accounts.working.name, (
                    f"Working account is set to '{profile.accounts.working.name}' ",
                    f"while should be '{working_account}'.",
                )

    def assert_in_tracked_accounts(self, account_names: Iterable[str] | None = None) -> None:
        tracked_account_names = [account.name for account in self.profile.accounts.tracked]
        self._assert_account_presence(tracked_account_names, account_names, "Tracked")

    def assert_not_in_tracked_accounts(self, account_names: Iterable[str] | None = None) -> None:
        tracked_account_names = [account.name for account in self.profile.accounts.tracked]
        self._assert_account_absence(tracked_account_names, account_names, "Tracked")

    def assert_in_known_accounts(self, account_names: Iterable[str] | None = None) -> None:
        known_account_names = [account.name for account in self.profile.accounts.known]
        self._assert_account_presence(known_account_names, account_names, "Known")

    def assert_not_in_known_accounts(self, account_names: Iterable[str] | None = None) -> None:
        known_account_names = [account.name for account in self.profile.accounts.known]
        self._assert_account_absence(known_account_names, account_names, "Known")

    def _assert_account_presence(
        self,
        actual_accounts: Iterable[str],
        expected_accounts: Iterable[str] | None,
        account_type: Literal["Tracked", "Known"],
    ) -> None:
        """Assert presence of accounts in a list of account."""
        if not expected_accounts:
            return

        expected_accounts_ = list(expected_accounts)
        actual_accounts_ = list(actual_accounts)
        for account in expected_accounts_:
            assert account in actual_accounts_, (
                f"{account_type} account '{account}' is missing while should be present.\n"
                f"Expected: {expected_accounts_} to be present in: {actual_accounts_}"
            )

    def _assert_account_absence(
        self,
        actual_accounts: Iterable[str],
        absence_accounts: Iterable[str] | None,
        account_type: Literal["Tracked", "Known"],
    ) -> None:
        """Assert absence of accounts in a list of account."""
        if not absence_accounts:
            return

        absence_accounts_ = list(absence_accounts)
        actual_accounts_ = list(actual_accounts)
        for account in absence_accounts_:
            assert account not in actual_accounts_, (
                f"{account_type} account '{account}' is present while should not be.\n"
                f"Expected: {absence_accounts_} not to be present in: {actual_accounts_}"
            )


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
