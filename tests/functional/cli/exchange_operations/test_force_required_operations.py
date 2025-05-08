from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.cli.exceptions import CLITransactionToExchangeError
from clive.__private.models.schemas import TransferFromSavingsOperation, TransferToSavingsOperation
from clive.__private.validators.exchange_operations_validator import ExchangeOperationsValidatorCli
from clive_local_tools.cli.checkers import assert_output_contains
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.helpers import create_transaction_file, get_formatted_error_message
from clive_local_tools.testnet_block_log import WORKING_ACCOUNT_NAME
from clive_local_tools.testnet_block_log.constants import KNOWN_EXCHANGES_NAMES

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from clive_local_tools.cli.cli_tester import CLITester


AMOUNT: Final[tt.Asset.HiveT] = tt.Asset.Hive(1)
KNOWN_EXCHANGE_NAME: Final[str] = KNOWN_EXCHANGES_NAMES[0]


@pytest.fixture
def transaction_with_forceable_operation_path(tmp_path: Path) -> Path:
    operations = [
        TransferToSavingsOperation(
            from_=WORKING_ACCOUNT_NAME,
            to=KNOWN_EXCHANGE_NAME,
            amount=tt.Asset.Hive(1),
            memo="transfer_to_savings_operation forceable test",
        ),
        TransferFromSavingsOperation(
            from_=WORKING_ACCOUNT_NAME,
            to=KNOWN_EXCHANGE_NAME,
            amount=tt.Asset.Hive(1),
            memo="transfer_from_savings_operation forceable test",
            request_id=1234,
        ),
    ]
    return create_transaction_file(tmp_path, operations)


def _assert_operation_to_exchange(send_operation_cb: Callable[[], None], *, force: bool) -> None:
    if force:
        send_operation_cb()
    else:
        expected_error_msg = get_formatted_error_message(
            CLITransactionToExchangeError(ExchangeOperationsValidatorCli.UNSAFE_EXCHANGE_OPERATION_MSG_ERROR)
        )
        with pytest.raises(CLITestCommandError) as error:
            send_operation_cb()
        assert_output_contains(expected_error_msg, error.value.stdout)


@pytest.mark.parametrize("force", [True, False])
async def test_loading_transaction(
    cli_tester: CLITester, transaction_with_forceable_operation_path: Path, *, force: bool
) -> None:
    # ARRANGE
    def send_operation() -> None:
        cli_tester.process_transaction(
            from_file=transaction_with_forceable_operation_path,
            sign=WORKING_ACCOUNT_KEY_ALIAS,
            force=force,
        )

    # ACT & ASSERT
    _assert_operation_to_exchange(send_operation, force=force)


@pytest.mark.parametrize("force", [True, False])
async def test_validate_of_performing_recurrent_transfer_to_exchange(cli_tester: CLITester, *, force: bool) -> None:
    # ARRANGE
    def send_operation() -> None:
        cli_tester.process_transfer_schedule_create(
            to=KNOWN_EXCHANGE_NAME,
            amount=AMOUNT,
            sign=WORKING_ACCOUNT_KEY_ALIAS,
            repeat=2,
            frequency="24h",
            force=force,
        )

    # ACT & ASSERT
    _assert_operation_to_exchange(send_operation, force=force)


@pytest.mark.parametrize("force", [True, False])
async def test_validate_of_performing_withdrawing_to_exchange(cli_tester: CLITester, *, force: bool) -> None:
    # ARRANGE
    def send_operation() -> None:
        request_id: int = 4123
        cli_tester.process_savings_withdrawal(
            to=KNOWN_EXCHANGE_NAME, amount=AMOUNT, sign=WORKING_ACCOUNT_KEY_ALIAS, force=force, request_id=request_id
        )

    # ACT & ASSERT
    _assert_operation_to_exchange(send_operation, force=force)


@pytest.mark.parametrize("force", [True, False])
async def test_validate_of_performing_deposit_to_exchange(cli_tester: CLITester, *, force: bool) -> None:
    # ARRANGE
    def send_operation() -> None:
        cli_tester.process_savings_deposit(
            to=KNOWN_EXCHANGE_NAME,
            amount=AMOUNT,
            sign=WORKING_ACCOUNT_KEY_ALIAS,
            force=force,
        )

    # ACT & ASSERT
    _assert_operation_to_exchange(send_operation, force=force)


@pytest.mark.parametrize("force", [True, False])
async def test_validation_of_powering_up_to_exchange(cli_tester: CLITester, *, force: bool) -> None:
    # ARRANGE
    def send_operation() -> None:
        cli_tester.process_power_up(
            amount=AMOUNT,
            to=KNOWN_EXCHANGE_NAME,
            sign=WORKING_ACCOUNT_KEY_ALIAS,
            force=force,
        )

    # ACT & ASSERT
    _assert_operation_to_exchange(send_operation, force=force)


@pytest.mark.parametrize("force", [True, False])
async def test_validate_of_performing_delegation_set_to_exchange(cli_tester: CLITester, *, force: bool) -> None:
    # ARRANGE
    def send_operation() -> None:
        cli_tester.process_delegations_set(
            delegatee=KNOWN_EXCHANGE_NAME,
            amount=AMOUNT,
            sign=WORKING_ACCOUNT_KEY_ALIAS,
            force=force,
        )

    # ACT & ASSERT
    _assert_operation_to_exchange(send_operation, force=force)


@pytest.mark.parametrize("force", [True, False])
async def test_validate_of_performing_of_withdrawal_routes_set_to_exchange(
    cli_tester: CLITester, *, force: bool
) -> None:
    # ARRANGE
    def send_operation() -> None:
        percent: int = 30
        cli_tester.process_withdraw_routes_set(
            to=KNOWN_EXCHANGE_NAME,
            percent=percent,
            sign=WORKING_ACCOUNT_KEY_ALIAS,
            force=force,
        )

    # ACT & ASSERT
    _assert_operation_to_exchange(send_operation, force=force)
