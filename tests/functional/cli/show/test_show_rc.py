from __future__ import annotations

from typing import TYPE_CHECKING, Final

import test_tools as tt

from clive_local_tools.cli.checkers import assert_output_contains
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.testnet_block_log.constants import EMPTY_ACCOUNT, WATCHED_ACCOUNTS_DATA

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


RC_DELEGATION_AMOUNT: Final[tt.Asset.VestT] = tt.Asset.Vest(5_000)
DELEGATEE_ACCOUNT_NAME: Final[str] = WATCHED_ACCOUNTS_DATA[0].account.name


async def test_show_rc_empty_account(cli_tester: CLITester) -> None:
    # ACT
    result = cli_tester.show_rc(account_name=EMPTY_ACCOUNT.name)

    # ASSERT
    assert_output_contains("No outgoing RC delegations", result)


async def test_show_rc_with_delegation(cli_tester: CLITester) -> None:
    # ARRANGE
    cli_tester.process_rc_delegations_set(
        delegatee=DELEGATEE_ACCOUNT_NAME, amount=RC_DELEGATION_AMOUNT, sign_with=WORKING_ACCOUNT_KEY_ALIAS
    )

    # ACT
    result = cli_tester.show_rc()

    # ASSERT
    assert_output_contains(DELEGATEE_ACCOUNT_NAME, result)
