from __future__ import annotations

from typing import TYPE_CHECKING, Final

from clive_local_tools.cli.checkers import assert_memo_key
from clive_local_tools.data.constants import WATCHED_ACCOUNTS, WORKING_ACCOUNT, WORKING_ACCOUNT_KEY_ALIAS

if TYPE_CHECKING:
    from clive_local_tools.cli.testing_cli import TestingCli
    from schemas.fields.basic import PublicKey


ALICE_MEMO_KEY: Final[PublicKey] = WORKING_ACCOUNT.public_key
OTHER_MEMO_KEY: Final[PublicKey] = WATCHED_ACCOUNTS[0].public_key


async def test_set_memo_key(testing_cli: TestingCli) -> None:
    # ACT
    getattr(testing_cli, "process_update-memo-key")(
        password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS, key=ALICE_MEMO_KEY
    )

    # ASSERT
    assert_memo_key(testing_cli, ALICE_MEMO_KEY)


async def test_set_memo_key_no_broadcast(testing_cli: TestingCli) -> None:
    # ACT
    result = getattr(testing_cli, "process_update-memo-key")(
        "--no-broadcast", password=WORKING_ACCOUNT.name, key=OTHER_MEMO_KEY
    )

    # ASSERT
    assert OTHER_MEMO_KEY in result.stdout
    assert_memo_key(testing_cli, ALICE_MEMO_KEY)


async def test_set_other_memo_key(testing_cli: TestingCli) -> None:
    # ACT
    getattr(testing_cli, "process_update-memo-key")(
        password=WORKING_ACCOUNT.name,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        key=OTHER_MEMO_KEY,
    )

    # ASSERT
    assert_memo_key(testing_cli, OTHER_MEMO_KEY)
