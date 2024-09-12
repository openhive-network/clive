from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.cli.exceptions import BEEKEEPER_PASSWORD_OR_SESSION_TOKEN_MUST_BE_SET_MESSAGE
from clive_local_tools.checkers import assert_operations_placed_in_blockchain
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS, WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_NAME
from schemas.operations import TransferOperation

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester

import test_tools as tt

RECEIVER: Final[str] = WATCHED_ACCOUNTS_DATA[0].account.name
AMOUNT: Final[tt.Asset.HiveT] = tt.Asset.Hive(1)
MEMO: Final[str] = "test-process-transfer-memo"


async def test_process_transfer(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Check clive process transfer command."""
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
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        password=WORKING_ACCOUNT_PASSWORD,
        memo=MEMO,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_process_transfer_required_password(cli_tester: CLITester) -> None:
    """Check if clive process transfer requires password."""
    # ARRANGE
    message = BEEKEEPER_PASSWORD_OR_SESSION_TOKEN_MUST_BE_SET_MESSAGE

    #  ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester.process_transfer(
            from_=WORKING_ACCOUNT_NAME,
            amount=tt.Asset.Hive(1),
            to=RECEIVER,
            sign=WORKING_ACCOUNT_KEY_ALIAS,
        )
