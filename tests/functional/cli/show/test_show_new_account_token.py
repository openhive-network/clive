from __future__ import annotations

from typing import TYPE_CHECKING

from clive_local_tools.cli.checkers import assert_new_account_tokens
from clive_local_tools.data.constants import (
    WORKING_ACCOUNT_KEY_ALIAS,
    WORKING_ACCOUNT_PASSWORD,
)

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


async def test_no_tokens(cli_tester: CLITester) -> None:
    # ARRNGE
    # ACT

    # ASSERT
    assert_new_account_tokens(cli_tester, tokens_amount=0)


async def test_one_token(cli_tester: CLITester) -> None:
    # ARRNGE
    cli_tester.process_claim_new_account_token(password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS)

    # ACT
    # ASSERT
    assert_new_account_tokens(cli_tester, tokens_amount=1)
