from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.cli.exceptions import (
    CLITransactionAutoSignUsedTogetherWithSignWithError,
    CLITransactionSignWithKeyNoKeysAvailableError,
    CLITransactionSignWithKeyNotSelectedError,
)
from clive.__private.core.keys.keys import PrivateKey
from clive.__private.models.schemas import TransferOperation
from clive_local_tools.checkers.blockchain_checkers import (
    assert_operations_placed_in_blockchain,
)
from clive_local_tools.cli import checkers
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from pathlib import Path

    from clive_local_tools.cli.cli_tester import CLITester

import test_tools as tt

RECEIVER: Final[str] = WATCHED_ACCOUNTS_DATA[0].account.name
AMOUNT: Final[tt.Asset.HiveT] = tt.Asset.Hive(1)
MEMO: Final[str] = "test-process-transfer-autosign-single-key"


async def test_autosign_when_there_is_no_sign_with(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    # ARRANGE
    operation = TransferOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        amount=AMOUNT,
        memo=MEMO,
    )

    # ACT
    result = cli_tester.process_transfer(
        from_=WORKING_ACCOUNT_NAME,
        amount=tt.Asset.Hive(1),
        to=RECEIVER,
        memo=MEMO,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_autosign_failure_due_to_no_keys_in_profile(
    cli_tester: CLITester,
) -> None:
    # ARRANGE
    cli_tester.configure_key_remove(alias=WORKING_ACCOUNT_KEY_ALIAS)

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=CLITransactionSignWithKeyNoKeysAvailableError.MESSAGE):
        cli_tester.process_transfer(
            from_=WORKING_ACCOUNT_NAME,
            amount=tt.Asset.Hive(1),
            to=RECEIVER,
            memo=MEMO,
        )


async def test_autosign_failure_due_to_multiple_keys_in_profile(
    cli_tester: CLITester,
) -> None:
    # ARRANGE
    pk = PrivateKey.create()
    cli_tester.configure_key_add(key=pk.value, alias="add_key")

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=CLITransactionSignWithKeyNotSelectedError.MESSAGE):
        cli_tester.process_transfer(
            from_=WORKING_ACCOUNT_NAME,
            amount=tt.Asset.Hive(1),
            to=RECEIVER,
            memo=MEMO,
        )


async def test_no_broadcasting_autosigned_operation(cli_tester: CLITester) -> None:
    # ACT
    result = cli_tester.process_transfer(
        from_=WORKING_ACCOUNT_NAME,
        amount=tt.Asset.Hive(1),
        to=RECEIVER,
        memo=MEMO,
        broadcast=False,
    )

    # ASSERT
    checkers.assert_no_exit_code_error(result)


async def test_usage_of_autosign_with_sign_with(
    cli_tester: CLITester,
) -> None:
    # ARRANGE

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=CLITransactionAutoSignUsedTogetherWithSignWithError.MESSAGE):
        cli_tester.process_transfer(
            from_=WORKING_ACCOUNT_NAME,
            amount=tt.Asset.Hive(1),
            to=RECEIVER,
            memo=MEMO,
            autosign=True,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        )


@pytest.mark.parametrize("autosign", [True, False])
async def test_saving_autosigned_operation_to_file(
    cli_tester: CLITester,
    tmp_path: Path,
    *,
    autosign: bool,
) -> None:
    # ARRANGE
    save_file = tmp_path / "saved_transaction.txt"

    # ACT
    result = cli_tester.process_transfer(
        from_=WORKING_ACCOUNT_NAME,
        amount=tt.Asset.Hive(1),
        to=RECEIVER,
        memo=MEMO,
        save_file=save_file,
        broadcast=False,
        autosign=autosign,
    )

    # ASSERT
    checkers.assert_no_exit_code_error(result)
    checkers.assert_signatures_in_transaction_file(save_file, signatures_count=autosign)
