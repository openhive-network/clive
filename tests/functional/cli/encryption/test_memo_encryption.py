from __future__ import annotations

from typing import TYPE_CHECKING, Final

import test_tools as tt

from clive.__private.models.schemas import TransferOperation
from clive_local_tools.checkers.blockchain_checkers import (
    assert_operations_placed_in_blockchain,
    assert_transaction_in_blockchain,
)
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.helpers import get_transaction_id_from_output
from clive_local_tools.testnet_block_log.constants import (
    ENCRYPTED_MEMO_CONTENT,
    WATCHED_ACCOUNTS_DATA,
    WORKING_ACCOUNT_NAME,
)

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester

RECEIVER: Final[str] = WATCHED_ACCOUNTS_DATA[0].account.name
AMOUNT: Final[tt.Asset.HiveT] = tt.Asset.Hive(1)


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

    # Get the transaction to check the memo
    transaction_id = get_transaction_id_from_output(result.stdout)
    node.wait_number_of_blocks(1)
    transaction = node.api.account_history.get_transaction(id_=transaction_id, include_reversible=True)

    # Find the transfer operation
    for op in transaction.operations:
        if isinstance(op.value, TransferOperation):
            assert op.value.memo.startswith("#"), "Encrypted memos start with '#' followed by the encoded key data"
            assert len(op.value.memo) > len(memo_content), (
                "The encrypted memo should be longer than the original (contains keys + encrypted content)"
            )
            break
    else:
        raise AssertionError("Transfer operation not found in transaction")


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
    """Check clive crypt decrypt command correctly decrypts the memo from testnet block_log."""
    # ARRANGE - Find the encrypted memo from block_log
    # The encrypted memo is a transfer from alice to bob created during block_log generation

    # Wait for blocks to be processed
    node.wait_number_of_blocks(1)

    account_history = node.api.account_history.get_account_history(
        account=WORKING_ACCOUNT_NAME,
        start=-1,
        limit=1000,
        include_reversible=True,
    )

    # Find the transfer operation with encrypted memo
    encrypted_memo = None
    for entry in account_history.history:
        op = entry[1].op
        # Check if this is a transfer with an encrypted memo (starts with '#')
        if (
            isinstance(op.value, TransferOperation)
            and op.value.memo
            and op.value.memo.startswith("#")
            and len(op.value.memo) > 1
        ):
            encrypted_memo = op.value.memo
            break

    assert encrypted_memo is not None, "Encoded text not found in block_log"

    # ACT
    result = cli_tester.crypt_decrypt(encrypted_memo=encrypted_memo)

    # ASSERT
    assert ENCRYPTED_MEMO_CONTENT in result.stdout, (
        f"Decrypted content does not match expected content, excepted {ENCRYPTED_MEMO_CONTENT}, got {result.stdout}"
    )
