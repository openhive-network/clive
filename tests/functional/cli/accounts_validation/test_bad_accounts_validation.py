from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

import pytest
import test_tools as tt

from clive.__private.cli.exceptions import CLITransactionBadAccountError
from clive.__private.core.accounts.account_manager import AccountManager
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.helpers import get_formatted_error_message
from clive_local_tools.testnet_block_log import WATCHED_ACCOUNTS_NAMES, WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from collections.abc import Callable, Generator

    from clive_local_tools.cli.cli_tester import CLITester

    from .conftest import ActionSelector

AMOUNT: Final[tt.Asset.HiveT] = tt.Asset.Hive(10)
BAD_ACCOUNT: Final[str] = AccountManager.get_bad_accounts()[0]
TEMPORARY_BAD_ACCOUNT: Final[str] = WATCHED_ACCOUNTS_NAMES[0]
EXPECTED_BAD_ACCOUNT_ERROR_MESSAGE = get_formatted_error_message(CLITransactionBadAccountError(BAD_ACCOUNT))


@pytest.fixture
def transaction_with_bad_account_path(tmp_path: Path) -> Path:
    transaction_with_bad_account_path = tmp_path / "trx.json"
    transaction_with_bad_account = {
        "ref_block_num": 601,
        "ref_block_prefix": 2633350841,
        "expiration": "2025-02-05T10:29:33",
        "extensions": [],
        "operations": [
            {
                "type": "transfer_operation",
                "value": {
                    "from": WORKING_ACCOUNT_NAME,
                    "to": BAD_ACCOUNT,
                    "amount": {"amount": "1000", "precision": 3, "nai": "@@000000021"},
                    "memo": "bad account test",
                },
            }
        ],
    }

    with Path(transaction_with_bad_account_path).open("w") as f:
        json.dump(transaction_with_bad_account, f)
    return transaction_with_bad_account_path


@contextmanager
def extended_bad_account_names(bad_account_to_add: str) -> Generator[Any, None, None]:
    with pytest.MonkeyPatch.context() as monkeypatch:
        original_bad_accounts_names = AccountManager.get_bad_accounts()
        extended_bad_accounts_names = [*original_bad_accounts_names, bad_account_to_add]
        monkeypatch.setattr(AccountManager, "_BAD_ACCOUNT_NAMES", extended_bad_accounts_names)
        assert AccountManager.is_account_bad(bad_account_to_add), "Temporary bad account should be in the list"
        yield
        monkeypatch.setattr(AccountManager, "_BAD_ACCOUNT_NAMES", original_bad_accounts_names)


def _assert_no_validation_of_bad_account(send_operation_cb: Callable[[], None]) -> None:
    """Temporarily add an account to the bad account list and perform operation."""
    with extended_bad_account_names(TEMPORARY_BAD_ACCOUNT):
        send_operation_cb()


def _assert_validation_of_bad_accounts(perform_operation_cb: Callable[[], None]) -> None:
    with pytest.raises(CLITestCommandError, match=EXPECTED_BAD_ACCOUNT_ERROR_MESSAGE):
        perform_operation_cb()


async def test_validation_of_delegate_vesting_shares(
    cli_tester: CLITester, process_action_selector: ActionSelector
) -> None:
    # ARRANGE
    def perform_operation() -> None:
        cli_tester.process_delegations_set(
            delegatee=BAD_ACCOUNT,
            amount=AMOUNT,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
            **process_action_selector,
        )

    # ACT & ASSERT
    _assert_validation_of_bad_accounts(perform_operation)


async def test_validation_of_setting_withdrawal_routes(
    cli_tester: CLITester, process_action_selector: ActionSelector
) -> None:
    # ARRANGE
    percent: int = 30

    def perform_operation() -> None:
        cli_tester.process_withdraw_routes_set(
            to=BAD_ACCOUNT,
            percent=percent,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
            **process_action_selector,
        )

    # ACT & ASSERT
    _assert_validation_of_bad_accounts(perform_operation)


async def test_validation_of_savings_withdrawal(cli_tester: CLITester, process_action_selector: ActionSelector) -> None:
    # ARRANGE
    def perform_operation() -> None:
        cli_tester.process_savings_withdrawal(
            to=BAD_ACCOUNT,
            amount=AMOUNT,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
            **process_action_selector,
        )

    # ACT & ASSERT
    _assert_validation_of_bad_accounts(perform_operation)


async def test_validation_of_deposing_savings(cli_tester: CLITester, process_action_selector: ActionSelector) -> None:
    # ARRANGE
    def perform_operation() -> None:
        cli_tester.process_savings_deposit(
            to=BAD_ACCOUNT,
            amount=AMOUNT,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
            **process_action_selector,
        )

    # ACT & ASSERT
    _assert_validation_of_bad_accounts(perform_operation)


async def test_validation_of_powering_up(cli_tester: CLITester, process_action_selector: ActionSelector) -> None:
    # ARRANGE
    def perform_operation() -> None:
        cli_tester.process_power_up(
            amount=AMOUNT,
            to=BAD_ACCOUNT,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
            **process_action_selector,
        )

    # ACT & ASSERT
    _assert_validation_of_bad_accounts(perform_operation)


async def test_validation_of_transfer(cli_tester: CLITester, process_action_selector: ActionSelector) -> None:
    # ARRANGE
    def perform_operation() -> None:
        cli_tester.process_transfer(
            to=BAD_ACCOUNT,
            amount=AMOUNT,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
            **process_action_selector,
        )

    # ACT & ASSERT
    _assert_validation_of_bad_accounts(perform_operation)


async def test_validation_of_setting_proxy(cli_tester: CLITester, process_action_selector: ActionSelector) -> None:
    # ARRANGE
    def perform_operation() -> None:
        cli_tester.process_proxy_set(
            proxy=BAD_ACCOUNT,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
            **process_action_selector,
        )

    # ACT & ASSERT
    _assert_validation_of_bad_accounts(perform_operation)


async def test_validation_of_creating_scheduled_transfer(
    cli_tester: CLITester, process_action_selector: ActionSelector
) -> None:
    # ARRANGE
    def perform_operation() -> None:
        cli_tester.process_transfer_schedule_create(
            to=BAD_ACCOUNT,
            amount=tt.Asset.Hive(1),
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
            repeat=2,
            frequency="24h",
            **process_action_selector,
        )

    # ACT & ASSERT
    _assert_validation_of_bad_accounts(perform_operation)


async def test_loading_transaction(cli_tester: CLITester, transaction_with_bad_account_path: Path) -> None:
    # ARRANGE
    def perform_operation() -> None:
        cli_tester.process_transaction(
            from_file=transaction_with_bad_account_path, sign_with=WORKING_ACCOUNT_KEY_ALIAS, broadcast=False
        )

    # ACT & ASSERT
    _assert_validation_of_bad_accounts(perform_operation)


async def test_no_validation_of_removing_withdraw_routes_to_account_that_become_bad(
    cli_tester: CLITester,
) -> None:
    """It should be possible to remove withdraw routes, even if account is on bad account list."""
    # ARRANGE
    percent: int = 30
    cli_tester.process_withdraw_routes_set(
        to=TEMPORARY_BAD_ACCOUNT, percent=percent, sign_with=WORKING_ACCOUNT_KEY_ALIAS
    )

    def send_operation() -> None:
        cli_tester.process_withdraw_routes_remove(to=TEMPORARY_BAD_ACCOUNT, sign_with=WORKING_ACCOUNT_KEY_ALIAS)

    # ACT & ASSERT
    _assert_no_validation_of_bad_account(send_operation)


async def test_no_validation_of_removing_delegation_of_vesting_shares_to_account_that_become_bad(
    cli_tester: CLITester,
) -> None:
    """It should be possible to remove delegation, even if account is on bad account list."""
    # ARRANGE
    cli_tester.process_delegations_set(
        delegatee=TEMPORARY_BAD_ACCOUNT, amount=AMOUNT, sign_with=WORKING_ACCOUNT_KEY_ALIAS
    )

    def send_operation() -> None:
        cli_tester.process_delegations_remove(delegatee=TEMPORARY_BAD_ACCOUNT, sign_with=WORKING_ACCOUNT_KEY_ALIAS)

    # ACT & ASSERT
    _assert_no_validation_of_bad_account(send_operation)


async def test_no_validation_of_canceling_savings_withdrawal_to_account_that_become_bad(
    cli_tester: CLITester,
) -> None:
    """It should be possible to cancel savings withdrawal, even if account is on bad account list."""
    # ARRANGE
    request_id = 1  # there is already one withdrawal pending in the block log

    cli_tester.process_savings_withdrawal(
        to=TEMPORARY_BAD_ACCOUNT, amount=AMOUNT, sign_with=WORKING_ACCOUNT_KEY_ALIAS, request_id=request_id
    )

    def send_operation() -> None:
        cli_tester.process_savings_withdrawal_cancel(sign_with=WORKING_ACCOUNT_KEY_ALIAS, request_id=request_id)

    # ACT & ASSERT
    _assert_no_validation_of_bad_account(send_operation)


async def test_no_validation_of_canceling_proxy_to_account_that_become_bad(
    cli_tester: CLITester,
) -> None:
    """It should be possible of clearing proxy, even if account is on bad account list."""
    # ARRANGE
    cli_tester.process_proxy_set(proxy=TEMPORARY_BAD_ACCOUNT, sign_with=WORKING_ACCOUNT_KEY_ALIAS)

    def send_operation() -> None:
        cli_tester.process_proxy_clear(sign_with=WORKING_ACCOUNT_KEY_ALIAS)

    # ACT & ASSERT
    _assert_no_validation_of_bad_account(send_operation)


async def test_no_validation_of_removing_scheduled_transfer_to_account_that_become_bad(
    cli_tester: CLITester,
) -> None:
    """It should be possible of removing scheduled transfer, even if account is on bad account list."""
    # ARRANGE
    cli_tester.process_transfer_schedule_create(
        to=TEMPORARY_BAD_ACCOUNT,
        amount=AMOUNT,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        repeat=2,
        frequency="24h",
    )

    def send_operation() -> None:
        cli_tester.process_transfer_schedule_remove(to=TEMPORARY_BAD_ACCOUNT, sign_with=WORKING_ACCOUNT_KEY_ALIAS)

    # ACT & ASSERT
    _assert_no_validation_of_bad_account(send_operation)
