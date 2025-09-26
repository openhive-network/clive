from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.cli.exceptions import CLITransactionUnknownAccountError
from clive.__private.models.schemas import TransferOperation
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.helpers import create_transaction_file, get_formatted_error_message
from clive_local_tools.testnet_block_log.constants import KNOWN_ACCOUNTS, UNKNOWN_ACCOUNT, WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from clive_local_tools.cli.cli_tester import CLITester

    from .conftest import ActionSelector

AMOUNT: Final[tt.Asset.HiveT] = tt.Asset.Hive(10)
KNOWN_ACCOUNT: Final[str] = KNOWN_ACCOUNTS[0]
EXPECTED_UNKNOWN_ACCOUNT_ERROR_MSG: Final[str] = get_formatted_error_message(
    CLITransactionUnknownAccountError(UNKNOWN_ACCOUNT)
)


VALIDATION_RECEIVERS: Final[list[str]] = [UNKNOWN_ACCOUNT, KNOWN_ACCOUNT]
VALIDATION_IDS: Final[list[str]] = ["unknown_account", "known_account"]


def _assert_operation_to_unknown_account_fails(perform_operation_cb: Callable[[], None]) -> None:
    with pytest.raises(CLITestCommandError, match=EXPECTED_UNKNOWN_ACCOUNT_ERROR_MSG):
        perform_operation_cb()


def _assert_validation_of_known_accounts(perform_operation_cb: Callable[[], None], receiver: str) -> None:
    if receiver == UNKNOWN_ACCOUNT:
        _assert_operation_to_unknown_account_fails(perform_operation_cb)
    else:
        perform_operation_cb()


@pytest.mark.parametrize("receiver", VALIDATION_RECEIVERS, ids=VALIDATION_IDS)
async def test_validation_of_delegate_vesting_shares(
    cli_tester: CLITester, receiver: str, process_action_selector: ActionSelector
) -> None:
    # ARRANGE
    def perform_operation() -> None:
        cli_tester.process_delegations_set(
            delegatee=receiver, amount=AMOUNT, sign_with=WORKING_ACCOUNT_KEY_ALIAS, **process_action_selector
        )

    # ACT & ASSERT
    _assert_validation_of_known_accounts(perform_operation, receiver)


@pytest.mark.parametrize("receiver", VALIDATION_RECEIVERS, ids=VALIDATION_IDS)
async def test_validation_of_setting_withdrawal_routes(
    cli_tester: CLITester, receiver: str, process_action_selector: ActionSelector
) -> None:
    # ARRANGE
    def perform_operation() -> None:
        percent: int = 30
        cli_tester.process_withdraw_routes_set(
            to=receiver, percent=percent, sign_with=WORKING_ACCOUNT_KEY_ALIAS, **process_action_selector
        )

    # ACT & ASSERT
    _assert_validation_of_known_accounts(perform_operation, receiver)


@pytest.mark.parametrize("receiver", VALIDATION_RECEIVERS, ids=VALIDATION_IDS)
async def test_validation_of_savings_withdrawal(
    cli_tester: CLITester, receiver: str, process_action_selector: ActionSelector
) -> None:
    # ARRANGE
    def perform_operation() -> None:
        cli_tester.process_savings_withdrawal(
            to=receiver, amount=AMOUNT, sign_with=WORKING_ACCOUNT_KEY_ALIAS, **process_action_selector
        )

    # ACT & ASSERT
    _assert_validation_of_known_accounts(perform_operation, receiver)


@pytest.mark.parametrize("receiver", VALIDATION_RECEIVERS, ids=VALIDATION_IDS)
async def test_validation_of_deposing_savings(
    cli_tester: CLITester, receiver: str, process_action_selector: ActionSelector
) -> None:
    # ARRANGE
    def perform_operation() -> None:
        cli_tester.process_savings_deposit(
            to=receiver, amount=AMOUNT, sign_with=WORKING_ACCOUNT_KEY_ALIAS, **process_action_selector
        )

    # ACT & ASSERT
    _assert_validation_of_known_accounts(perform_operation, receiver)


@pytest.mark.parametrize("receiver", VALIDATION_RECEIVERS, ids=VALIDATION_IDS)
async def test_validation_of_powering_up(
    cli_tester: CLITester, receiver: str, process_action_selector: ActionSelector
) -> None:
    # ARRANGE
    def perform_operation() -> None:
        cli_tester.process_power_up(
            amount=AMOUNT, to=receiver, sign_with=WORKING_ACCOUNT_KEY_ALIAS, **process_action_selector
        )

    # ACT & ASSERT
    _assert_validation_of_known_accounts(perform_operation, receiver)


async def test_validation_of_powering_up_to_self(
    cli_tester: CLITester, process_action_selector: ActionSelector
) -> None:
    # ARRANGE
    def perform_operation() -> None:
        cli_tester.process_power_up(amount=AMOUNT, sign_with=WORKING_ACCOUNT_KEY_ALIAS, **process_action_selector)

    # ACT & ASSERT
    _assert_validation_of_known_accounts(perform_operation, WORKING_ACCOUNT_NAME)


@pytest.mark.parametrize("receiver", VALIDATION_RECEIVERS, ids=VALIDATION_IDS)
async def test_validation_of_transfer(
    cli_tester: CLITester, receiver: str, process_action_selector: ActionSelector
) -> None:
    # ARRANGE
    def perform_operation() -> None:
        cli_tester.process_transfer(
            to=receiver, amount=AMOUNT, sign_with=WORKING_ACCOUNT_KEY_ALIAS, **process_action_selector
        )

    # ACT & ASSERT
    _assert_validation_of_known_accounts(perform_operation, receiver)


@pytest.mark.parametrize("receiver", VALIDATION_RECEIVERS, ids=VALIDATION_IDS)
async def test_validation_of_setting_proxy(
    cli_tester: CLITester, receiver: str, process_action_selector: ActionSelector
) -> None:
    # ARRANGE
    def perform_operation() -> None:
        cli_tester.process_proxy_set(proxy=receiver, sign_with=WORKING_ACCOUNT_KEY_ALIAS, **process_action_selector)

    # ACT & ASSERT
    _assert_validation_of_known_accounts(perform_operation, receiver)


@pytest.mark.parametrize("receiver", VALIDATION_RECEIVERS, ids=VALIDATION_IDS)
async def test_validation_of_creating_scheduled_transfer(
    cli_tester: CLITester, receiver: str, process_action_selector: ActionSelector
) -> None:
    # ARRANGE
    def perform_operation() -> None:
        cli_tester.process_transfer_schedule_create(
            to=receiver,
            amount=tt.Asset.Hive(1),
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
            repeat=2,
            frequency="24h",
            **process_action_selector,
        )

    # ACT & ASSERT
    _assert_validation_of_known_accounts(perform_operation, receiver)


@pytest.fixture
def transaction_path(tmp_path: Path, receiver: str) -> Path:
    operations = [
        TransferOperation(
            from_=WORKING_ACCOUNT_NAME,
            to=receiver,
            amount=tt.Asset.Hive(10),
            memo="known account test",
        )
    ]
    return create_transaction_file(tmp_path, operations)


@pytest.mark.parametrize("receiver", VALIDATION_RECEIVERS, ids=VALIDATION_IDS)
async def test_loading_transaction(cli_tester: CLITester, receiver: str, transaction_path: Path) -> None:
    # ARRANGE
    def perform_operation() -> None:
        cli_tester.process_transaction(from_file=transaction_path, sign_with=WORKING_ACCOUNT_KEY_ALIAS, broadcast=False)

    # ACT & ASSERT
    _assert_validation_of_known_accounts(perform_operation, receiver)


async def test_no_validation_of_removing_withdraw_routes_to_account_that_was_known(
    cli_tester: CLITester,
) -> None:
    """It should be possible to remove withdraw routes, even if account is not on known account list."""
    # ARRANGE
    percent: int = 30
    cli_tester.process_withdraw_routes_set(to=KNOWN_ACCOUNT, percent=percent, sign_with=WORKING_ACCOUNT_KEY_ALIAS)
    cli_tester.configure_known_account_remove(account_name=KNOWN_ACCOUNT)

    # ACT & ASSERT
    cli_tester.process_withdraw_routes_remove(to=KNOWN_ACCOUNT, sign_with=WORKING_ACCOUNT_KEY_ALIAS)


async def test_no_validation_of_removing_delegation_of_vesting_shares_to_account_that_was_known(
    cli_tester: CLITester,
) -> None:
    """It should be possible to remove delegation, even if account is not on known account list."""
    # ARRANGE
    cli_tester.process_delegations_set(delegatee=KNOWN_ACCOUNT, amount=AMOUNT, sign_with=WORKING_ACCOUNT_KEY_ALIAS)
    cli_tester.configure_known_account_remove(account_name=KNOWN_ACCOUNT)

    # ACT & ASSERT
    cli_tester.process_delegations_remove(delegatee=KNOWN_ACCOUNT, sign_with=WORKING_ACCOUNT_KEY_ALIAS)


async def test_no_validation_of_canceling_savings_withdrawal_to_account_that_was_known(
    cli_tester: CLITester,
) -> None:
    """It should be possible to cancel savings withdrawal, even if account is not on known account list."""
    # ARRANGE
    request_id = 1  # there is already one withdrawal pending in the block log

    cli_tester.process_savings_withdrawal(
        to=KNOWN_ACCOUNT, amount=AMOUNT, sign_with=WORKING_ACCOUNT_KEY_ALIAS, request_id=request_id
    )

    cli_tester.configure_known_account_remove(account_name=KNOWN_ACCOUNT)

    # ACT & ASSERT
    cli_tester.process_savings_withdrawal_cancel(sign_with=WORKING_ACCOUNT_KEY_ALIAS, request_id=request_id)


async def test_no_validation_of_canceling_proxy_to_account_that_was_known(
    cli_tester: CLITester,
) -> None:
    """It should be possible of clearing proxy, even if account is not on known account list."""
    # ARRANGE
    cli_tester.process_proxy_set(proxy=KNOWN_ACCOUNT, sign_with=WORKING_ACCOUNT_KEY_ALIAS)
    cli_tester.configure_known_account_remove(account_name=KNOWN_ACCOUNT)

    # ACT & ASSERT
    cli_tester.process_proxy_clear(sign_with=WORKING_ACCOUNT_KEY_ALIAS)


async def test_no_validation_of_removing_scheduled_transfer_to_account_that_was_known(
    cli_tester: CLITester,
) -> None:
    """It should be possible of removing scheduled transfer, even if account is not on known account list."""
    # ARRANGE
    cli_tester.process_transfer_schedule_create(
        to=KNOWN_ACCOUNT,
        amount=AMOUNT,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        repeat=2,
        frequency="24h",
    )
    cli_tester.configure_known_account_remove(account_name=KNOWN_ACCOUNT)

    # ACT & ASSERT
    cli_tester.process_transfer_schedule_remove(to=KNOWN_ACCOUNT, sign_with=WORKING_ACCOUNT_KEY_ALIAS)
