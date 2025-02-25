from __future__ import annotations

from typing import TYPE_CHECKING, Final

from clive_local_tools.cli.checkers import assert_memo_key
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.testnet_block_log import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_DATA

if TYPE_CHECKING:
    from clive.__private.models.schemas import PublicKey
    from clive_local_tools.cli.cli_tester import CLITester


ALICE_MEMO_KEY: Final[PublicKey] = WORKING_ACCOUNT_DATA.account.public_key
OTHER_MEMO_KEY: Final[PublicKey] = WATCHED_ACCOUNTS_DATA[0].account.public_key


async def test_set_memo_key(cli_tester: CLITester) -> None:
    # ACT
    cli_tester.process_update_memo_key(sign=WORKING_ACCOUNT_KEY_ALIAS, key=ALICE_MEMO_KEY)

    # ASSERT
    assert_memo_key(cli_tester, ALICE_MEMO_KEY)


async def test_set_memo_key_no_broadcast(cli_tester: CLITester) -> None:
    # ACT
    result = cli_tester.process_update_memo_key(broadcast=False, key=OTHER_MEMO_KEY)

    # ASSERT
    assert OTHER_MEMO_KEY in result.stdout, f"Transaction should set memo key to {OTHER_MEMO_KEY}"
    assert_memo_key(cli_tester, ALICE_MEMO_KEY)


async def test_set_other_memo_key(cli_tester: CLITester) -> None:
    # ACT
    cli_tester.process_update_memo_key(sign=WORKING_ACCOUNT_KEY_ALIAS, key=OTHER_MEMO_KEY)

    # ASSERT
    assert_memo_key(cli_tester, OTHER_MEMO_KEY)
