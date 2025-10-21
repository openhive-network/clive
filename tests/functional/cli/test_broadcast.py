from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.cli.exceptions import CLIMutuallyExclusiveOptionsError
from clive.__private.models.schemas import TransferOperation
from clive_local_tools.checkers.blockchain_checkers import assert_transaction_in_blockchain
from clive_local_tools.cli.checkers import (
    assert_contains_dry_run_message,
    assert_contains_transaction_broadcasted_message,
    assert_contains_transaction_saved_to_file_message,
    assert_does_not_contain_transaction_broadcasted_message,
)
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.helpers import create_transaction_file, create_transaction_filepath
from clive_local_tools.testnet_block_log import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from pathlib import Path

    from clive_local_tools.cli.cli_tester import CLITester

RECEIVER: Final[str] = WATCHED_ACCOUNTS_DATA[0].account.name
AMOUNT: Final[tt.Asset.HiveT] = tt.Asset.Hive(1)


@pytest.fixture
def transaction_file_with_transfer() -> Path:
    operation = TransferOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        amount=AMOUNT,
        memo="test broadcast",
    )

    return create_transaction_file(operation, "with_transfer")


def test_broadcasts_by_default_when_no_special_flags(node: tt.RawNode, cli_tester: CLITester) -> None:
    """Should broadcast by default when no special flags like --save-file are given."""
    # ACT
    result = cli_tester.process_transfer(to=RECEIVER, amount=AMOUNT)

    # ASSERT
    assert_contains_transaction_broadcasted_message(result.output)
    assert_transaction_in_blockchain(node, result)


def test_does_not_broadcast_when_saving_to_file(cli_tester: CLITester) -> None:
    """Should not broadcast by default when transaction is being saved to a file."""
    # ARRANGE
    transaction_file_path = create_transaction_filepath()

    # ACT
    result = cli_tester.process_transfer(to=RECEIVER, amount=AMOUNT, save_file=transaction_file_path)

    # ASSERT
    assert transaction_file_path.exists(), "Transaction file should be created."
    assert_contains_transaction_saved_to_file_message(transaction_file_path, result.output)
    assert_does_not_contain_transaction_broadcasted_message(result.output)


def test_broadcasts_when_explicitly_requested_even_with_save_file(node: tt.RawNode, cli_tester: CLITester) -> None:
    """Should broadcast if --broadcast is explicitly provided, even with --save-file."""
    # ARRANGE
    transaction_file_path = create_transaction_filepath()

    # ACT
    result = cli_tester.process_transfer(to=RECEIVER, amount=AMOUNT, save_file=transaction_file_path, broadcast=True)

    # ASSERT
    assert transaction_file_path.exists(), "Transaction file should be created."
    assert_contains_transaction_saved_to_file_message(transaction_file_path, result.output)
    assert_contains_transaction_broadcasted_message(result.output)
    assert_transaction_in_blockchain(node, result)


def test_broadcasts_transaction_from_file_by_default_when_no_special_flags(
    node: tt.RawNode, cli_tester: CLITester, transaction_file_with_transfer: Path
) -> None:
    """Should broadcast when reading a transaction from a file by default (no special flags)."""
    # ACT
    result = cli_tester.process_transaction(from_file=transaction_file_with_transfer)

    # ASSERT
    assert_contains_transaction_broadcasted_message(result.output)
    assert_transaction_in_blockchain(node, result)


def test_does_not_broadcast_when_force_unsign_is_used(
    cli_tester: CLITester, transaction_file_with_transfer: Path
) -> None:
    """Should not broadcast when --force-unsign is enabled."""
    # ACT
    result = cli_tester.process_transaction(from_file=transaction_file_with_transfer, force_unsign=True)

    # ASSERT
    assert_contains_dry_run_message(result.output)
    assert_does_not_contain_transaction_broadcasted_message(result.output)


def test_negative_does_not_broadcast_when_explicitly_required_with_force_unsign(
    cli_tester: CLITester, transaction_file_with_transfer: Path
) -> None:
    """Should not broadcast if --force-unsign is provided, even if --broadcast is explicitly requested."""
    # ACT && ASSERT
    with pytest.raises(CLITestCommandError, match=str(CLIMutuallyExclusiveOptionsError("broadcast", "force-unsign"))):
        cli_tester.process_transaction(from_file=transaction_file_with_transfer, force_unsign=True, broadcast=True)
