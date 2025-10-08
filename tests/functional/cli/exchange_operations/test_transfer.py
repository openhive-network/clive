from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.cli.exceptions import CLITransactionToExchangeError
from clive.__private.models.schemas import TransferOperation
from clive.__private.validators.exchange_operations_validator import (
    ExchangeOperationsValidatorCli,
)
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.helpers import create_transaction_file, get_formatted_error_message
from clive_local_tools.testnet_block_log import WORKING_ACCOUNT_NAME
from clive_local_tools.testnet_block_log.constants import KNOWN_EXCHANGES_NAMES

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from clive_local_tools.cli.cli_tester import CLITester

KNOWN_EXCHANGE_NAME: Final[str] = KNOWN_EXCHANGES_NAMES[0]
ACCOUNT_DOES_NOT_EXIST_ERROR_MSG: Final[str] = f"Account {KNOWN_EXCHANGE_NAME} doesn't exist"
MEMOLESS_TRANSFER_MSG_ERROR: Final[str] = get_formatted_error_message(
    CLITransactionToExchangeError(ExchangeOperationsValidatorCli.MEMOLESS_HIVE_TRANSFER_MSG_ERROR)
)

HBD_TRANSFER_OPERATION_MSG_ERROR: Final[str] = get_formatted_error_message(
    CLITransactionToExchangeError(ExchangeOperationsValidatorCli.HBD_TRANSFER_MSG_ERROR)
)

FORCE_REQUIRED_OPERATION_MSG_ERROR: Final[str] = get_formatted_error_message(
    CLITransactionToExchangeError(ExchangeOperationsValidatorCli.UNSAFE_EXCHANGE_OPERATION_MSG_ERROR)
)

MEMO_MSG: Final[str] = "test memo to exchange"
EMPTY_MEMO_MSG: Final[str] = ""


def _assert_operation_error(operation_cb: Callable[[], None], expected_message: str) -> None:
    with pytest.raises(CLITestCommandError, match=expected_message):
        operation_cb()


@pytest.fixture
def transaction_file_with_memoless_transfer() -> Path:
    operation = TransferOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=KNOWN_EXCHANGE_NAME,
        amount=tt.Asset.Hive(1000),
        memo=EMPTY_MEMO_MSG,
    )

    return create_transaction_file(operation, "memoless_transfer")


@pytest.fixture
def transaction_file_with_hbd_transfer() -> Path:
    operation = TransferOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=KNOWN_EXCHANGE_NAME,
        amount=tt.Asset.Hbd(1000),
        memo="HBD transfer to exchange",
    )

    return create_transaction_file(operation, "hbd_transfer")


@pytest.mark.parametrize("amount", [tt.Asset.Hive(10), tt.Asset.Hbd(10)])
async def test_validate_memoless_transfer_to_exchange(
    cli_tester: CLITester, amount: tt.Asset.HiveT | tt.Asset.HbdT
) -> None:
    """
    Verify that memoless transfer to exchange is not allowed.

    This test checks performing transfer that has no memo to exchange,
    it will generate an error, and transfer will not be broadcasted.
    """

    # ARRANGE
    def operation() -> None:
        cli_tester.process_transfer(
            to=KNOWN_EXCHANGE_NAME,
            amount=amount,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
            memo=EMPTY_MEMO_MSG,
        )

    # ACT & ASSERT
    _assert_operation_error(operation, MEMOLESS_TRANSFER_MSG_ERROR)


async def test_validate_performing_transaction_with_memoless_transfer_to_exchange(
    cli_tester: CLITester,
    transaction_file_with_memoless_transfer: Path,
) -> None:
    """
    Verify performing transaction memoless transfer to exchange.

    This test checks if transaction with memoless transfer to exchange is not allowed.
    It will generate an error, and transaction will not be broadcasted.
    """

    # ARRANGE
    def operation() -> None:
        cli_tester.process_transaction(
            from_file=transaction_file_with_memoless_transfer,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        )

    # ACT & ASSERT
    _assert_operation_error(operation, MEMOLESS_TRANSFER_MSG_ERROR)


async def test_validate_performing_transaction_with_hbd_transfer_to_exchange(
    cli_tester: CLITester,
    transaction_file_with_hbd_transfer: Path,
) -> None:
    """
    Verify performing transaction hbd transfer to exchange.

    This test checks if transaction with hbd transfer to exchange is not allowed.
    It will generate an error, and transaction will not be broadcasted.
    """

    # ARRANGE
    def operation() -> None:
        cli_tester.process_transaction(
            from_file=transaction_file_with_hbd_transfer,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        )

    # ACT & ASSERT
    _assert_operation_error(operation, HBD_TRANSFER_OPERATION_MSG_ERROR)


async def test_validate_hive_transfer_with_memo_to_exchange(
    cli_tester: CLITester,
) -> None:
    """HIVE transfers with memo are allowed to exchanges."""
    # ARRANGE
    amount = tt.Asset.Hive(10.000)

    # ACT & ASSERT
    cli_tester.process_transfer(
        to=KNOWN_EXCHANGE_NAME,
        amount=amount,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        memo=MEMO_MSG,
    )


async def test_validate_hbd_transfer_with_memo_to_exchange(
    cli_tester: CLITester,
) -> None:
    """HBD transfer operations to exchanges are not allowed."""
    # ARRANGE
    amount = tt.Asset.Hbd(10.000)

    def operation() -> None:
        cli_tester.process_transfer(
            to=KNOWN_EXCHANGE_NAME,
            amount=amount,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
            memo=MEMO_MSG,
        )

    # ACT & ASSERT
    _assert_operation_error(operation, HBD_TRANSFER_OPERATION_MSG_ERROR)
