from __future__ import annotations

from typing import TYPE_CHECKING, Final

import test_tools as tt

from clive_local_tools.cli.checkers import assert_no_removed_delegations, assert_pending_removed_delegations
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS, WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log.constants import EMPTY_ACCOUNT

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


AMOUNT_TO_DELEGATE: Final[tt.Asset.VestT] = tt.Asset.Vest(123_456.789)


async def test_pending_removed_delegations_none(cli_tester: CLITester) -> None:
    # ACT
    # ASSERT
    assert_no_removed_delegations(cli_tester)


async def test_pending_removed_delegations_basic(cli_tester: CLITester) -> None:
    # ARRANGE
    cli_tester.process_delegations_set(
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        delegatee=EMPTY_ACCOUNT.name,
        amount=AMOUNT_TO_DELEGATE,
    )
    cli_tester.process_delegations_remove(
        password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, delegatee=EMPTY_ACCOUNT.name
    )

    # ACT
    # ASSERT
    assert_pending_removed_delegations(cli_tester, AMOUNT_TO_DELEGATE)
