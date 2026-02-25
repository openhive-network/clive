from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.cli.exceptions import CLIInsufficientKeysAutoSignError
from clive.__private.models.schemas import CustomJsonOperation, JsonString, TransferOperation
from clive_local_tools.checkers.blockchain_checkers import assert_operations_placed_in_blockchain
from clive_local_tools.cli.checkers import (
    assert_contains_transaction_saved_to_file_message,
    assert_transaction_file_is_signed,
)
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.helpers import create_transaction_file, create_transaction_filepath, get_formatted_error_message
from clive_local_tools.testnet_block_log.constants import (
    WATCHED_ACCOUNTS_DATA,
    WATCHED_ACCOUNTS_NAMES,
    WORKING_ACCOUNT_NAME,
)

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


AMOUNT: Final[tt.Asset.HiveT] = tt.Asset.Hive(1)
BOB: Final[str] = WATCHED_ACCOUNTS_NAMES[0]
BOB_KEY_ALIAS: Final[str] = "bob_key"
BOB_PRIVATE_KEY: Final[str] = WATCHED_ACCOUNTS_DATA[0].account.private_key
TIMMY: Final[str] = WATCHED_ACCOUNTS_NAMES[1]
TIMMY_KEY_ALIAS: Final[str] = "timmy_key"
TIMMY_PRIVATE_KEY: Final[str] = WATCHED_ACCOUNTS_DATA[1].account.private_key
CUSTOM_JSON_ID: Final[str] = "test-autosign-multi-auth"
CUSTOM_JSON_BODY: Final[str] = '{"action": "test", "payload": {"key": "value", "nested": [1, 2, 3]}}'


async def test_autosign_transaction_with_multiple_operations_from_different_accounts(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test that autosign correctly signs a transaction containing operations from multiple accounts."""
    # ARRANGE
    cli_tester.configure_key_add(key=BOB_PRIVATE_KEY, alias=BOB_KEY_ALIAS)

    op_alice_to_bob = TransferOperation(from_=WORKING_ACCOUNT_NAME, to=BOB, amount=AMOUNT, memo="alice sends")
    op_bob_to_alice = TransferOperation(from_=BOB, to=WORKING_ACCOUNT_NAME, amount=AMOUNT, memo="bob sends")
    transaction_file = create_transaction_file([op_alice_to_bob, op_bob_to_alice], "multi_account")

    signed_file = create_transaction_filepath("multi_account_signed")

    # ACT
    result = cli_tester.process_transaction(
        from_file=transaction_file,
        save_file=signed_file,
        broadcast=True,
    )

    # ASSERT
    assert_contains_transaction_saved_to_file_message(signed_file, result.stdout)
    assert_transaction_file_is_signed(signed_file, signatures_count=2)
    assert_operations_placed_in_blockchain(node, result, op_alice_to_bob, op_bob_to_alice)


async def test_negative_autosign_multi_account_transaction_with_insufficient_keys(
    cli_tester: CLITester,
) -> None:
    """Test that autosign fails when wallet has only some of the keys required by a multi-account transaction."""
    # ARRANGE - profile has only alice's key, but transaction requires both alice's and bob's active authority
    op_alice_to_bob = TransferOperation(from_=WORKING_ACCOUNT_NAME, to=BOB, amount=AMOUNT, memo="alice sends")
    op_bob_to_alice = TransferOperation(from_=BOB, to=WORKING_ACCOUNT_NAME, amount=AMOUNT, memo="bob sends")
    transaction_file = create_transaction_file([op_alice_to_bob, op_bob_to_alice], "multi_account_insufficient")

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=get_formatted_error_message(CLIInsufficientKeysAutoSignError())):
        cli_tester.process_transaction(from_file=transaction_file, broadcast=True)


async def test_autosign_custom_json_with_multiple_required_active_auths(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test autosign on custom_json requiring active authority from multiple accounts."""
    # ARRANGE
    cli_tester.configure_key_add(key=BOB_PRIVATE_KEY, alias=BOB_KEY_ALIAS)
    cli_tester.configure_key_add(key=TIMMY_PRIVATE_KEY, alias=TIMMY_KEY_ALIAS)

    operation = CustomJsonOperation(
        required_auths=[WORKING_ACCOUNT_NAME, BOB, TIMMY],
        required_posting_auths=[],
        id_=CUSTOM_JSON_ID,
        json_=JsonString(CUSTOM_JSON_BODY),
    )
    transaction_file = create_transaction_file([operation], "custom_json_multi_active_auth")
    signed_file = create_transaction_filepath("custom_json_multi_active_auth_signed")

    # ACT
    result = cli_tester.process_transaction(
        from_file=transaction_file,
        save_file=signed_file,
        broadcast=True,
    )

    # ASSERT
    assert_contains_transaction_saved_to_file_message(signed_file, result.stdout)
    assert_transaction_file_is_signed(signed_file, signatures_count=3)
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_autosign_mixed_custom_json_and_transfer_from_different_accounts(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test autosign on transaction mixing custom_json (active auth) with transfer from a different account."""
    # ARRANGE
    cli_tester.configure_key_add(key=BOB_PRIVATE_KEY, alias=BOB_KEY_ALIAS)

    custom_json_op = CustomJsonOperation(
        required_auths=[WORKING_ACCOUNT_NAME],
        required_posting_auths=[],
        id_=CUSTOM_JSON_ID,
        json_=JsonString(CUSTOM_JSON_BODY),
    )
    transfer_op = TransferOperation(from_=BOB, to=WORKING_ACCOUNT_NAME, amount=AMOUNT, memo="bob sends")
    transaction_file = create_transaction_file([custom_json_op, transfer_op], "mixed_custom_json_transfer")
    signed_file = create_transaction_filepath("mixed_custom_json_transfer_signed")

    # ACT
    result = cli_tester.process_transaction(
        from_file=transaction_file,
        save_file=signed_file,
        broadcast=True,
    )

    # ASSERT
    assert_contains_transaction_saved_to_file_message(signed_file, result.stdout)
    assert_transaction_file_is_signed(signed_file, signatures_count=2)
    assert_operations_placed_in_blockchain(node, result, custom_json_op, transfer_op)
