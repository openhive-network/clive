from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.cli.exceptions import CLITransactionBadAccountError, CLITransactionUnknownAccountError
from clive.__private.core.accounts.account_manager import _load_bad_accounts_from_file
from clive_local_tools.cli.checkers import assert_output_contains
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.helpers import get_formatted_error_message
from clive_local_tools.testnet_block_log.constants import KNOWN_ACCOUNTS, UNKNOWN_ACCOUNT, WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from clive_local_tools.cli.cli_tester import CLITester

AMOUNT: Final[tt.Asset.HiveT] = tt.Asset.Hive(10)
KNOWN_ACCOUNT: Final[str] = KNOWN_ACCOUNTS[0]
BAD_ACCOUNT: Final[str] = _load_bad_accounts_from_file()[0]
EXPECTED_UNKNOWN_ACCOUNT_ERROR_MSG: Final[str] = get_formatted_error_message(
    CLITransactionUnknownAccountError(UNKNOWN_ACCOUNT)
)
EXPECTED_BAD_ACCOUNT_ERROR_MESSAGE = get_formatted_error_message(CLITransactionBadAccountError(BAD_ACCOUNT))

VALIDATION_RECEIVERS: Final[list[str]] = [UNKNOWN_ACCOUNT, KNOWN_ACCOUNT, BAD_ACCOUNT]
VALIDATION_IDS: Final[list[str]] = ["unknown_account", "known_account", "bad_account"]


@pytest.fixture(params=["broadcast", "save_file"])
def save_file_path_or_none(tmp_path: Path, request: pytest.FixtureRequest) -> Path | None:
    if request.param == "broadcast":
        return None
    return tmp_path / "trx.json"


def _assert_operation_to_bad_account_fails(perform_operation_cb: Callable[[], None]) -> None:
    with pytest.raises(CLITestCommandError) as error:
        perform_operation_cb()
    assert_output_contains(EXPECTED_BAD_ACCOUNT_ERROR_MESSAGE, error.value.stdout)


def _assert_operation_to_unknown_account_fails(perform_operation_cb: Callable[[], None]) -> None:
    with pytest.raises(CLITestCommandError) as error:
        perform_operation_cb()
    assert_output_contains(EXPECTED_UNKNOWN_ACCOUNT_ERROR_MSG, error.value.stdout)


def _assert_validation_of_accounts(perform_operation_cb: Callable[[], None], receiver: str) -> None:
    if receiver == UNKNOWN_ACCOUNT:
        _assert_operation_to_unknown_account_fails(perform_operation_cb)
    elif receiver == BAD_ACCOUNT:
        _assert_operation_to_bad_account_fails(perform_operation_cb)
    else:
        perform_operation_cb()


@pytest.mark.parametrize("receiver", VALIDATION_RECEIVERS, ids=VALIDATION_IDS)
async def test_validation_of_delegate_vesting_shares(
    cli_tester: CLITester, receiver: str, save_file_path_or_none: Path | None
) -> None:
    # ARRANGE
    def perform_operation() -> None:
        cli_tester.process_delegations_set(
            delegatee=receiver,
            amount=AMOUNT,
            sign=WORKING_ACCOUNT_KEY_ALIAS,
            broadcast=True if save_file_path_or_none is None else None,
            save_file=save_file_path_or_none if save_file_path_or_none is not None else None,
        )

    # ACT & ASSERT
    _assert_validation_of_accounts(perform_operation, receiver)


@pytest.mark.parametrize("receiver", VALIDATION_RECEIVERS, ids=VALIDATION_IDS)
async def test_validation_of_setting_withdrawal_routes(
    cli_tester: CLITester, receiver: str, save_file_path_or_none: Path | None
) -> None:
    # ARRANGE
    def perform_operation() -> None:
        percent: int = 30
        cli_tester.process_withdraw_routes_set(
            to=receiver,
            percent=percent,
            sign=WORKING_ACCOUNT_KEY_ALIAS,
            broadcast=True if save_file_path_or_none is None else None,
            save_file=save_file_path_or_none if save_file_path_or_none is not None else None,
        )

    # ACT & ASSERT
    _assert_validation_of_accounts(perform_operation, receiver)


@pytest.mark.parametrize("receiver", VALIDATION_RECEIVERS, ids=VALIDATION_IDS)
async def test_validation_of_savings_withdrawal(
    cli_tester: CLITester, receiver: str, save_file_path_or_none: Path | None
) -> None:
    # ARRANGE
    def perform_operation() -> None:
        cli_tester.process_savings_withdrawal(
            to=receiver,
            amount=AMOUNT,
            sign=WORKING_ACCOUNT_KEY_ALIAS,
            broadcast=True if save_file_path_or_none is None else None,
            save_file=save_file_path_or_none if save_file_path_or_none is not None else None,
        )

    # ACT & ASSERT
    _assert_validation_of_accounts(perform_operation, receiver)


@pytest.mark.parametrize("receiver", VALIDATION_RECEIVERS, ids=VALIDATION_IDS)
async def test_validation_of_deposing_savings(
    cli_tester: CLITester, receiver: str, save_file_path_or_none: Path | None
) -> None:
    # ARRANGE
    def perform_operation() -> None:
        cli_tester.process_savings_deposit(
            to=receiver,
            amount=AMOUNT,
            sign=WORKING_ACCOUNT_KEY_ALIAS,
            broadcast=True if save_file_path_or_none is None else None,
            save_file=save_file_path_or_none if save_file_path_or_none is not None else None,
        )

    # ACT & ASSERT
    _assert_validation_of_accounts(perform_operation, receiver)


@pytest.mark.parametrize("receiver", VALIDATION_RECEIVERS, ids=VALIDATION_IDS)
async def test_validation_of_powering_up(
    cli_tester: CLITester, receiver: str, save_file_path_or_none: Path | None
) -> None:
    # ARRANGE
    def perform_operation() -> None:
        cli_tester.process_power_up(
            amount=AMOUNT,
            to=receiver,
            sign=WORKING_ACCOUNT_KEY_ALIAS,
            broadcast=True if save_file_path_or_none is None else None,
            save_file=save_file_path_or_none if save_file_path_or_none is not None else None,
        )

    # ACT & ASSERT
    _assert_validation_of_accounts(perform_operation, receiver)


async def test_validation_of_powering_up_to_self(cli_tester: CLITester) -> None:
    # ARRANGE
    def perform_operation() -> None:
        cli_tester.process_power_up(amount=AMOUNT, sign=WORKING_ACCOUNT_KEY_ALIAS)

    # ACT & ASSERT
    _assert_validation_of_accounts(perform_operation, WORKING_ACCOUNT_NAME)


@pytest.mark.parametrize("receiver", VALIDATION_RECEIVERS, ids=VALIDATION_IDS)
async def test_validation_of_transfer(
    cli_tester: CLITester, receiver: str, save_file_path_or_none: Path | None
) -> None:
    # ARRANGE
    def perform_operation() -> None:
        cli_tester.process_transfer(
            to=receiver,
            amount=AMOUNT,
            sign=WORKING_ACCOUNT_KEY_ALIAS,
            broadcast=True if save_file_path_or_none is None else None,
            save_file=save_file_path_or_none if save_file_path_or_none is not None else None,
        )

    # ACT & ASSERT
    _assert_validation_of_accounts(perform_operation, receiver)


@pytest.mark.parametrize("receiver", VALIDATION_RECEIVERS, ids=VALIDATION_IDS)
async def test_validation_of_setting_proxy(
    cli_tester: CLITester, receiver: str, save_file_path_or_none: Path | None
) -> None:
    # ARRANGE
    def perform_operation() -> None:
        cli_tester.process_proxy_set(
            proxy=receiver,
            sign=WORKING_ACCOUNT_KEY_ALIAS,
            broadcast=True if save_file_path_or_none is None else None,
            save_file=save_file_path_or_none if save_file_path_or_none is not None else None,
        )

    # ACT & ASSERT
    _assert_validation_of_accounts(perform_operation, receiver)


@pytest.mark.parametrize("receiver", VALIDATION_RECEIVERS, ids=VALIDATION_IDS)
async def test_validation_of_creating_scheduled_transfer(
    cli_tester: CLITester, receiver: str, save_file_path_or_none: Path | None
) -> None:
    # ARRANGE
    def perform_operation() -> None:
        cli_tester.process_transfer_schedule_create(
            to=receiver,
            amount=tt.Asset.Hive(1),
            sign=WORKING_ACCOUNT_KEY_ALIAS,
            repeat=2,
            frequency="24h",
            broadcast=True if save_file_path_or_none is None else None,
            save_file=save_file_path_or_none if save_file_path_or_none is not None else None,
        )

    # ACT & ASSERT
    _assert_validation_of_accounts(perform_operation, receiver)


async def test_no_validation_of_removing_withdraw_routes_to_account_that_was_known(
    cli_tester: CLITester,
) -> None:
    """It should be possible to remove withdraw routes, even if account is not on known account list."""
    # ARRANGE
    percent: int = 30
    cli_tester.process_withdraw_routes_set(to=KNOWN_ACCOUNT, percent=percent, sign=WORKING_ACCOUNT_KEY_ALIAS)
    cli_tester.configure_known_account_remove(account_name=KNOWN_ACCOUNT)

    # ACT & ASSERT
    cli_tester.process_withdraw_routes_remove(to=KNOWN_ACCOUNT, sign=WORKING_ACCOUNT_KEY_ALIAS)


async def test_no_validation_of_removing_delegation_of_vesting_shares_to_account_that_was_known(
    cli_tester: CLITester,
) -> None:
    """It should be possible to remove delegation, even if account is not on known account list."""
    # ARRANGE
    cli_tester.process_delegations_set(delegatee=KNOWN_ACCOUNT, amount=AMOUNT, sign=WORKING_ACCOUNT_KEY_ALIAS)
    cli_tester.configure_known_account_remove(account_name=KNOWN_ACCOUNT)

    # ACT & ASSERT
    cli_tester.process_delegations_remove(delegatee=KNOWN_ACCOUNT, sign=WORKING_ACCOUNT_KEY_ALIAS)


async def test_no_validation_of_canceling_savings_withdrawal_to_account_that_was_known(
    cli_tester: CLITester,
) -> None:
    """It should be possible to cancel savings withdrawal, even if account is not on known account list."""
    # ARRANGE
    request_id: int = 0
    cli_tester.process_savings_withdrawal(
        to=KNOWN_ACCOUNT, amount=AMOUNT, sign=WORKING_ACCOUNT_KEY_ALIAS, request_id=request_id
    )
    cli_tester.configure_known_account_remove(account_name=KNOWN_ACCOUNT)

    # ACT & ASSERT
    cli_tester.process_savings_withdrawal_cancel(sign=WORKING_ACCOUNT_KEY_ALIAS, request_id=request_id)


async def test_no_validation_of_canceling_proxy_to_account_that_was_known(
    cli_tester: CLITester,
) -> None:
    """It should be possible of clearing proxy, even if account is not on known account list."""
    # ARRANGE
    cli_tester.process_proxy_set(proxy=KNOWN_ACCOUNT, sign=WORKING_ACCOUNT_KEY_ALIAS)
    cli_tester.configure_known_account_remove(account_name=KNOWN_ACCOUNT)

    # ACT & ASSERT
    cli_tester.process_proxy_clear(sign=WORKING_ACCOUNT_KEY_ALIAS)


async def test_no_validation_of_removing_scheduled_transfer_to_account_that_was_known(
    cli_tester: CLITester,
) -> None:
    """It should be possible of removing scheduled transfer, even if account is not on known account list."""
    # ARRANGE
    cli_tester.process_transfer_schedule_create(
        to=KNOWN_ACCOUNT,
        amount=AMOUNT,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        repeat=2,
        frequency="24h",
    )
    cli_tester.configure_known_account_remove(account_name=KNOWN_ACCOUNT)

    # ACT & ASSERT
    cli_tester.process_transfer_schedule_remove(to=KNOWN_ACCOUNT, sign=WORKING_ACCOUNT_KEY_ALIAS)
