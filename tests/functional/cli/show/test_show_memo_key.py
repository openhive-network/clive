from __future__ import annotations

from typing import TYPE_CHECKING

from clive_local_tools.cli.checkers import assert_memo_key
from clive_local_tools.data.constants import WORKING_ACCOUNT

if TYPE_CHECKING:
    from clive_local_tools.cli.testing_cli import TestingCli


async def test_show_memo_key_basic(testing_cli: TestingCli) -> None:
    # ACT
    # ASSERT
    assert_memo_key(testing_cli, WORKING_ACCOUNT.public_key)
