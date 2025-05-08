from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.cli.exceptions import CLIMemolessTransferToExchangeError
from clive.__private.core.constants.node import EMPTY_MEMO_VALUE
from clive_local_tools.cli.checkers import assert_output_contains
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.helpers import get_formatted_error_message
from clive_local_tools.testnet_block_log import WORKING_ACCOUNT_NAME
from clive_local_tools.testnet_block_log.constants import KNOWN_EXCHANGES_NAMES

from .conftest import get_current_date_time

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester

KNOWN_EXCHANGE_NAME: Final[str] = KNOWN_EXCHANGES_NAMES[0]


@pytest.fixture
def transaction_with_memoless_transfer_path(tmp_path: Path) -> Path:
    transaction_with_memoless_transfer_path = tmp_path / "trx.json"
    transaction_with_memoless_transfer = {
        "ref_block_num": 601,
        "expiration": get_current_date_time(),
        "extensions": [],
        "operations": [
            {
                "type": "transfer_operation",
                "value": {
                    "from": WORKING_ACCOUNT_NAME,
                    "to": KNOWN_EXCHANGE_NAME,
                    "amount": {"amount": "1000", "precision": 3, "nai": "@@000000021"},
                    "memo": EMPTY_MEMO_VALUE,
                },
            },
            {
                "type": "transfer_from_savings_operation",
                "value": {
                    "from": WORKING_ACCOUNT_NAME,
                    "to": KNOWN_EXCHANGE_NAME,
                    "amount": {"amount": "1000", "precision": 3, "nai": "@@000000021"},
                    "memo": "transfer_from_savings_operation forceable test",
                    "request_id": 0,
                },
            },
        ],
    }

    with Path(transaction_with_memoless_transfer_path).open("w") as f:
        json.dump(transaction_with_memoless_transfer, f)
    return transaction_with_memoless_transfer_path


async def test_validate_memoless_transfer_to_exchange(cli_tester: CLITester) -> None:
    """
    Verify that memoless transfer to exchange is not allowed.

    This test checks performing transfer that has no memo to exchange,
    it will generate an error, and transfer will not be broadcasted.
    """
    # ARRANGE
    amount = tt.Asset.Hive(10.000)
    expected_error_message = get_formatted_error_message(CLIMemolessTransferToExchangeError(KNOWN_EXCHANGE_NAME))

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError) as error:
        cli_tester.process_transfer(
            to=KNOWN_EXCHANGE_NAME, amount=amount, sign=WORKING_ACCOUNT_KEY_ALIAS, memo=EMPTY_MEMO_VALUE
        )
    assert_output_contains(expected_error_message, error.value.stdout)


async def test_validate_performing_transaction_with_memoless_transfer_to_exchange(
    cli_tester: CLITester,
    transaction_with_memoless_transfer_path: Path,
) -> None:
    """
    Verify performing transaction memoless transfer to exchange.

    This test checks if transaction with memoless transfer to exchange is not allowed.
    It will generate an error, and transaction will not be broadcasted.
    """
    # ARRANGE
    expected_error_message = get_formatted_error_message(CLIMemolessTransferToExchangeError(KNOWN_EXCHANGE_NAME))

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError) as error:
        cli_tester.process_transaction(
            from_file=transaction_with_memoless_transfer_path,
            sign=WORKING_ACCOUNT_KEY_ALIAS,
        )
    assert_output_contains(expected_error_message, error.value.stdout)


async def test_validate_transfer_with_memo_to_exchange(cli_tester: CLITester) -> None:
    """Only transfers with memo are allowed to exchanges."""
    # ARRANGE
    amount = tt.Asset.Hive(10.000)
    expected_error_msg = f"Account {KNOWN_EXCHANGE_NAME} doesn't exist"
    memo = "test memo to exchange"

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=expected_error_msg):
        cli_tester.process_transfer(to=KNOWN_EXCHANGE_NAME, amount=amount, sign=WORKING_ACCOUNT_KEY_ALIAS, memo=memo)
