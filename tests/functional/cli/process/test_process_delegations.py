from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive_local_tools.cli.checkers import assert_delegations, assert_no_delegations
from clive_local_tools.data.constants import (
    WATCHED_ACCOUNTS,
    WORKING_ACCOUNT,
    WORKING_ACCOUNT_KEY_ALIAS,
    WORKING_ACCOUNT_PASSWORD,
)

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester
    from schemas.fields.basic import PublicKey



AMOUNT_TO_DELEGATE: Final[tt.Asset.HiveT] = tt.Asset.Vest(2345.678)
DELEGATEE_ACCOUNT: Final[tt.Account] = WATCHED_ACCOUNTS[0]


async def test_delegations_set(cli_tester: CLITester) -> None:
    # ACT
    cli_tester.process_delegations_set(
        password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, delegatee=DELEGATEE_ACCOUNT.name, amount=AMOUNT_TO_DELEGATE
    )

    # ASSERT
    assert_delegations(cli_tester, delegatee=DELEGATEE_ACCOUNT.name, amount=AMOUNT_TO_DELEGATE)


async def test_delegations_remove(cli_tester: CLITester) -> None:
    # ARRANGE
    cli_tester.process_delegations_set(
        password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, delegatee=DELEGATEE_ACCOUNT.name, amount=AMOUNT_TO_DELEGATE
    )

    # ACT
    cli_tester.process_delegations_remove(
        password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, delegatee=DELEGATEE_ACCOUNT.name
    )

    # ASSERT
    assert_no_delegations(cli_tester)
