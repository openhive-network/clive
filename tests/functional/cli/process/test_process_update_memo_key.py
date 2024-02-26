from __future__ import annotations

from typing import TYPE_CHECKING

from clive_local_tools.cli.checkers import assert_memo_key
from clive_local_tools.data.constants import WATCHED_ACCOUNTS, WORKING_ACCOUNT, WORKING_ACCOUNT_KEY_ALIAS

if TYPE_CHECKING:
    from clive_local_tools.cli.testing_cli import TestingCli


other_account = WATCHED_ACCOUNTS[0]
alice_memo_key = WORKING_ACCOUNT.public_key
other_memo_key = other_account.public_key


async def test_set_memo_key(testing_cli: TestingCli) -> None:
    # ACT
    getattr(testing_cli, "process_update-memo-key")(
        password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS, key=alice_memo_key
    )

    # ASSERT
    assert_memo_key(testing_cli, alice_memo_key)


async def test_set_memo_key_no_broadcast(testing_cli: TestingCli) -> None:
    # ACT
    result = getattr(testing_cli, "process_update-memo-key")(
        "--no-broadcast", password=WORKING_ACCOUNT.name, key=other_memo_key
    )

    # ASSERT
    assert other_memo_key in result.stdout
    assert_memo_key(testing_cli, alice_memo_key)


async def test_set_other_memo_key(testing_cli: TestingCli) -> None:
    # ACT
    getattr(testing_cli, "process_update-memo-key")(
        password=WORKING_ACCOUNT.name,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        key=other_memo_key,
    )

    # ASSERT
    assert_memo_key(testing_cli, other_memo_key)
