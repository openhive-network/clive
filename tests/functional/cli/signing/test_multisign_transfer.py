from __future__ import annotations

from typing import TYPE_CHECKING, Final

import test_tools as tt

from clive.__private.core.keys.keys import PrivateKey
from clive_local_tools.checkers.blockchain_checkers import assert_transaction_in_blockchain
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester

RECEIVER: Final[str] = WATCHED_ACCOUNTS_DATA[0].account.name
AMOUNT: Final[tt.Asset.HiveT] = tt.Asset.Hive(1)
SECOND_KEY_ALIAS: Final[str] = "second_active_key"


async def test_multisign_transfer(node: tt.RawNode, cli_tester: CLITester) -> None:
    """Test that a transfer can be signed with multiple keys when active authority threshold requires it."""
    # ARRANGE
    second_private_key = PrivateKey.generate()
    second_public_key = second_private_key.calculate_public_key()

    cli_tester.configure_key_add(key=second_private_key.value, alias=SECOND_KEY_ALIAS)

    cli_tester.process_update_authority(
        "active",
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        threshold=2,
    ).add_key(
        key=second_public_key.value,
        weight=1,
    ).fire()

    node.wait_number_of_blocks(1)

    # ACT
    result = cli_tester.process_transfer(
        from_=WORKING_ACCOUNT_NAME,
        amount=AMOUNT,
        to=RECEIVER,
        sign_with=[WORKING_ACCOUNT_KEY_ALIAS, SECOND_KEY_ALIAS],
    )

    # ASSERT
    assert_transaction_in_blockchain(node, result)
