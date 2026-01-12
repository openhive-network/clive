from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.cli.commands.abc.memo_command import CLIEncryptMemoKeyNotImportedError
from clive.__private.cli.commands.crypto.decrypt import (
    CLIDecryptMemoKeyNotImportedError,
    CLIInvalidEncryptedMemoFormatError,
)
from clive.__private.core.keys.keys import PrivateKey, PrivateKeyAliased
from clive.__private.models.schemas import TransferOperation
from clive_local_tools.checkers.blockchain_checkers import (
    assert_operations_placed_in_blockchain,
    assert_transaction_in_blockchain,
)
from clive_local_tools.cli.checkers import assert_memo_key
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import ALT_WORKING_ACCOUNT1_KEY_ALIAS, WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.helpers import (
    get_formatted_error_message,
    get_operation_from_transaction,
    get_transaction_id_from_output,
)
from clive_local_tools.testnet_block_log.constants import (
    ACCOUNT_WITH_ENCRYPTED_MEMO_DATA,
    ENCRYPTED_MEMO_CONTENT,
    WATCHED_ACCOUNTS_DATA,
    WORKING_ACCOUNT_NAME,
)

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester

RECEIVER: Final[str] = WATCHED_ACCOUNTS_DATA[0].account.name
AMOUNT: Final[tt.Asset.HiveT] = tt.Asset.Hive(1)


def get_encrypted_memo_from_block_log(node: tt.RawNode) -> str:
    """Get the encrypted memo from the pregenerated block_log."""
    account_history = node.api.account_history.get_account_history(
        account=ACCOUNT_WITH_ENCRYPTED_MEMO_DATA.account.name,
    )

    for entry in account_history.history:
        operation = entry[1].op
        # Encrypted memo by convention starts with '#'
        if isinstance(operation.value, TransferOperation) and operation.value.memo.startswith("#"):
            return operation.value.memo

    pytest.fail("Encrypted memo not found in block_log")


async def test_process_transfer_with_encrypted_memo(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Check clive process transfer command encrypts memo when it starts with '#'."""
    # ARRANGE
    memo_content = "#This is a secret memo"

    # ACT
    result = cli_tester.process_transfer(
        from_=WORKING_ACCOUNT_NAME,
        amount=AMOUNT,
        to=RECEIVER,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        memo=memo_content,
    )

    # ASSERT - the memo should be encrypted (starts with '#' followed by encoded data)
    assert result.exit_code == 0

    # Verify the transaction was placed in blockchain
    assert_transaction_in_blockchain(node, result)

    # Get the operation and check the memo
    transaction_id = get_transaction_id_from_output(result.stdout)
    op = get_operation_from_transaction(node, transaction_id, TransferOperation)

    # Assert the memo is encrypted
    assert op.memo.startswith("#"), "Encrypted memos start with '#' followed by the encoded key data"
    assert len(op.memo) > len(memo_content), (
        "The encrypted memo should be longer than the original (contains keys + encrypted content)"
    )


async def test_process_transfer_with_plain_memo(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Check clive process transfer command does NOT encrypt memo when it doesn't start with '#'."""
    # ARRANGE
    memo_content = "This is a plain memo"
    operation = TransferOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        amount=AMOUNT,
        memo=memo_content,
    )

    # ACT
    result = cli_tester.process_transfer(
        from_=WORKING_ACCOUNT_NAME,
        amount=AMOUNT,
        to=RECEIVER,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        memo=memo_content,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_decrypt_memo_from_block_log(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Check clive crypto decrypt command correctly decrypts the memo from testnet block_log."""
    # ARRANGE
    # Import memo key needed for decrypting
    cli_tester.world.profile.keys.add_to_import(
        PrivateKeyAliased(
            value=ACCOUNT_WITH_ENCRYPTED_MEMO_DATA.account.private_key, alias=ALT_WORKING_ACCOUNT1_KEY_ALIAS
        )
    )
    await cli_tester.world.commands.sync_data_with_beekeeper()

    encrypted_memo = get_encrypted_memo_from_block_log(node)

    # ACT
    result = cli_tester.crypto_decrypt(encrypted_memo=encrypted_memo)

    # ASSERT
    assert ENCRYPTED_MEMO_CONTENT in result.stdout, (
        f"Decrypted content does not match expected content, excepted {ENCRYPTED_MEMO_CONTENT}, got {result.stdout}"
    )


async def test_negative_transfer_with_encrypted_memo_when_no_memo_key_imported(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Check that clive process transfer fails when trying to encrypt memo without having the memo key imported."""
    # ARRANGE
    memo_content = "#This is other secret memo"

    # Change memo key to a new key but don't import to beekeeper to test failure case
    new_memo_key = PrivateKey.generate().calculate_public_key()
    cli_tester.process_update_memo_key(account_name=WORKING_ACCOUNT_NAME, key=new_memo_key.value)

    # Verify the memo key was updated
    node.wait_number_of_blocks(1)
    assert_memo_key(cli_tester, new_memo_key.value)

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=get_formatted_error_message(CLIEncryptMemoKeyNotImportedError())):
        cli_tester.process_transfer(
            from_=WORKING_ACCOUNT_NAME,
            amount=AMOUNT,
            to=RECEIVER,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
            memo=memo_content,
        )


async def test_negative_decrypt_memo_fails_without_memo_key(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Check that clive crypto decrypt fails when the memo key is not imported."""
    # ARRANGE
    # Do NOT import memo key - this is intentional to test the failure case
    encrypted_memo = get_encrypted_memo_from_block_log(node)

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=get_formatted_error_message(CLIDecryptMemoKeyNotImportedError())):
        cli_tester.crypto_decrypt(encrypted_memo=encrypted_memo)


async def test_negative_decrypt_memo_fails_with_invalid_format(cli_tester: CLITester) -> None:
    """Check that clive crypto decrypt fails when the memo doesn't start with '#'."""
    # ARRANGE
    invalid_memo = "This is not an encrypted memo"

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=get_formatted_error_message(CLIInvalidEncryptedMemoFormatError())):
        cli_tester.crypto_decrypt(encrypted_memo=invalid_memo)
