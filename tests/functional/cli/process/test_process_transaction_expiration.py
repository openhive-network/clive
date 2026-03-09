from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.models.schemas import TransferOperation
from clive_local_tools.checkers.blockchain_checkers import (
    assert_operations_placed_in_blockchain,
    assert_transaction_in_blockchain,
)
from clive_local_tools.cli.checkers import assert_transaction_file_is_unsigned
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.cli.helpers import load_transaction_from_file
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.helpers import create_transaction_filepath
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from pathlib import Path

    from clive_local_tools.cli.cli_tester import CLITester


RECEIVER: Final[str] = WATCHED_ACCOUNTS_DATA[0].account.name
AMOUNT: Final[tt.Asset.HiveT] = tt.Asset.Hive(1)


@pytest.fixture
def unsigned_transaction_file(cli_tester: CLITester) -> Path:
    """Create an unsigned transaction file with a transfer operation."""
    transaction_filepath = create_transaction_filepath("unsigned_for_expiration")
    cli_tester.process_transfer(
        amount=AMOUNT,
        to=RECEIVER,
        broadcast=False,
        save_file=transaction_filepath,
        autosign=False,
    )
    return transaction_filepath


@pytest.fixture
def signed_transaction_file(cli_tester: CLITester) -> Path:
    """Create a signed transaction file with a transfer operation."""
    transaction_filepath = create_transaction_filepath("signed_for_expiration")
    cli_tester.process_transfer(
        amount=AMOUNT,
        to=RECEIVER,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        broadcast=False,
        save_file=transaction_filepath,
    )
    return transaction_filepath


async def test_process_transaction_update_metadata_with_force_unsign(
    cli_tester: CLITester, unsigned_transaction_file: Path
) -> None:
    """Check if --update-metadata with --force-unsign on an unsigned transaction refreshes metadata."""
    # ARRANGE
    original_transaction = load_transaction_from_file(unsigned_transaction_file)
    output_filepath = create_transaction_filepath("updated_metadata")

    # Set a custom expiration in the profile
    cli_tester.configure_transaction_expiration_set("1h")

    # ACT
    cli_tester.process_transaction(
        from_file=unsigned_transaction_file,
        update_metadata=True,
        force_unsign=True,
        save_file=output_filepath,
    )

    # ASSERT
    updated_transaction = load_transaction_from_file(output_filepath)
    assert_transaction_file_is_unsigned(output_filepath)

    # Metadata should have been refreshed - expiration should be different
    assert updated_transaction.expiration != original_transaction.expiration, (
        "Transaction expiration should have been updated after --update-metadata."
    )


async def test_process_transaction_update_metadata_with_override_mode(
    cli_tester: CLITester, signed_transaction_file: Path
) -> None:
    """Check if --update-metadata with --already-signed-mode=override refreshes metadata and re-signs."""
    # ARRANGE
    original_transaction = load_transaction_from_file(signed_transaction_file)
    output_filepath = create_transaction_filepath("override_metadata")

    # Set a custom expiration in the profile
    cli_tester.configure_transaction_expiration_set("2h")

    # ACT
    cli_tester.process_transaction(
        from_file=signed_transaction_file,
        update_metadata=True,
        already_signed_mode="override",
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        broadcast=False,
        save_file=output_filepath,
    )

    # ASSERT
    updated_transaction = load_transaction_from_file(output_filepath)
    assert updated_transaction.expiration != original_transaction.expiration, (
        "Transaction expiration should have been updated after --update-metadata."
    )
    assert updated_transaction.is_signed, "Transaction should be re-signed after override."


async def test_process_transaction_update_metadata_and_broadcast(
    node: tt.RawNode, cli_tester: CLITester, unsigned_transaction_file: Path
) -> None:
    """Check if --update-metadata refreshes metadata, signs and broadcasts successfully."""
    # ARRANGE
    cli_tester.configure_transaction_expiration_set("1h")

    # ACT
    result = cli_tester.process_transaction(
        from_file=unsigned_transaction_file,
        update_metadata=True,
        already_signed_mode="override",
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_transaction_in_blockchain(node, result)


async def test_negative_process_transaction_update_metadata_signed_without_override(
    cli_tester: CLITester, signed_transaction_file: Path
) -> None:
    """Check if --update-metadata with a signed transaction without --already-signed-mode=override raises an error."""
    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match="--update-metadata"):
        cli_tester.process_transaction(
            from_file=signed_transaction_file,
            update_metadata=True,
        )


async def test_process_transaction_update_metadata_signed_with_force_unsign(
    cli_tester: CLITester, signed_transaction_file: Path
) -> None:
    """Check if --update-metadata with --force-unsign strips signatures and refreshes metadata."""
    # ARRANGE
    original_transaction = load_transaction_from_file(signed_transaction_file)
    output_filepath = create_transaction_filepath("force_unsign_updated_metadata")

    # Set a custom expiration in the profile
    cli_tester.configure_transaction_expiration_set("1h")

    # ACT
    cli_tester.process_transaction(
        from_file=signed_transaction_file,
        update_metadata=True,
        force_unsign=True,
        save_file=output_filepath,
    )

    # ASSERT
    updated_transaction = load_transaction_from_file(output_filepath)
    assert_transaction_file_is_unsigned(output_filepath)
    assert updated_transaction.expiration != original_transaction.expiration, (
        "Transaction expiration should have been updated after --update-metadata."
    )


async def test_process_transfer_with_custom_expiration(cli_tester: CLITester) -> None:
    """Check if process transfer uses profile's transaction expiration when building a transaction."""
    # ARRANGE
    cli_tester.configure_transaction_expiration_set("1h")
    transaction_filepath = create_transaction_filepath("custom_expiration")

    # ACT
    cli_tester.process_transfer(
        amount=AMOUNT,
        to=RECEIVER,
        broadcast=False,
        save_file=transaction_filepath,
        autosign=False,
    )

    # ASSERT - expiration should be approximately 1 hour from now (not the default 30m)
    transaction = load_transaction_from_file(transaction_filepath)
    # Build a second transaction with default expiration to compare
    default_filepath = create_transaction_filepath("default_expiration")
    cli_tester.configure_transaction_expiration_set("30m")
    cli_tester.process_transfer(
        amount=AMOUNT,
        to=RECEIVER,
        broadcast=False,
        save_file=default_filepath,
        autosign=False,
    )
    default_transaction = load_transaction_from_file(default_filepath)

    assert transaction.expiration > default_transaction.expiration, (
        f"Transaction with 1h expiration ({transaction.expiration}) should expire later "
        f"than one with 30m expiration ({default_transaction.expiration})."
    )


async def test_process_transfer_with_min_expiration_broadcasts_successfully(
    node: tt.RawNode, cli_tester: CLITester
) -> None:
    """Check if a transfer with minimum expiration (3s) broadcasts successfully when done immediately."""
    # ARRANGE
    operation = TransferOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        amount=AMOUNT,
        memo="",
    )
    cli_tester.configure_transaction_expiration_set("3s")

    # ACT
    result = cli_tester.process_transfer(
        amount=AMOUNT,
        to=RECEIVER,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_process_transfer_with_min_expiration_expires(node: tt.RawNode, cli_tester: CLITester) -> None:
    """Check if a transaction with minimum expiration saved to file expires when time passes."""
    # ARRANGE
    cli_tester.configure_transaction_expiration_set("3s")
    transaction_filepath = create_transaction_filepath("min_expiration")
    cli_tester.process_transfer(
        amount=AMOUNT,
        to=RECEIVER,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        broadcast=False,
        save_file=transaction_filepath,
    )

    # Wait for the transaction to expire - 3s expiration means it will expire after ~1 block (3s)
    node.wait_number_of_blocks(2)

    # ACT & ASSERT - broadcasting an expired transaction should fail
    with pytest.raises(CLITestCommandError):
        cli_tester.process_transaction(
            from_file=transaction_filepath,
            already_signed_mode="multisign",
            autosign=False,
        )
