from __future__ import annotations

from typing import TYPE_CHECKING

import test_tools as tt

from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.testnet_block_log.constants import UNKNOWN_ACCOUNT

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


async def test_no_trasaction_validation_to_unknown_account(cli_tester: CLITester) -> None:
    """
    Verify that transaction to account that is not on known accounts list is allowed.

    This test checks that when a known account is disabled using
    `clive configure known-account disable`, it will allow to make
    transaction to the account that is no longer on known account list.
    """
    # ARRANGE
    amount = tt.Asset.Hive(10.000)
    cli_tester.configure_known_account_disable()

    # ACT & ASSERT
    cli_tester.process_delegations_set(delegatee=UNKNOWN_ACCOUNT, amount=amount, sign=WORKING_ACCOUNT_KEY_ALIAS)
