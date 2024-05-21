from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive_local_tools.cli.checkers import assert_delegations, assert_no_delegations
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS, WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_DATA

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


AMOUNT_TO_DELEGATE1: Final[tt.Asset.VestT] = tt.Asset.Vest(2345.678)
AMOUNT_TO_DELEGATE2: Final[tt.Asset.VestT] = tt.Asset.Vest(3456.789)
AMOUNT_TO_DELEGATE3: Final[tt.Asset.HiveT] = tt.Asset.Hive(4567.890)
DELEGATEE_ACCOUNT: Final[tt.Account] = WATCHED_ACCOUNTS_DATA[0].account


@pytest.mark.parametrize("amount_to_delegate", [AMOUNT_TO_DELEGATE1, AMOUNT_TO_DELEGATE3])
async def test_delegations_set(cli_tester: CLITester, amount_to_delegate: tt.Asset.HiveT | tt.Asset.VestT) -> None:
    # ACT
    cli_tester.process_delegations_set(
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        delegatee=DELEGATEE_ACCOUNT.name,
        amount=amount_to_delegate,
    )

    # ASSERT
    assert_delegations(cli_tester, delegatee=DELEGATEE_ACCOUNT.name, asset=amount_to_delegate)


async def test_delegations_reset(cli_tester: CLITester) -> None:
    # ARRANGE
    cli_tester.process_delegations_set(
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        delegatee=DELEGATEE_ACCOUNT.name,
        amount=AMOUNT_TO_DELEGATE1,
    )

    # ACT
    cli_tester.process_delegations_set(
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        delegatee=DELEGATEE_ACCOUNT.name,
        amount=AMOUNT_TO_DELEGATE2,
    )

    # ASSERT
    assert_delegations(cli_tester, delegatee=DELEGATEE_ACCOUNT.name, asset=AMOUNT_TO_DELEGATE2)


async def test_delegations_remove(cli_tester: CLITester) -> None:
    # ARRANGE
    cli_tester.process_delegations_set(
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        delegatee=DELEGATEE_ACCOUNT.name,
        amount=AMOUNT_TO_DELEGATE1,
    )

    # ACT
    cli_tester.process_delegations_remove(
        password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, delegatee=DELEGATEE_ACCOUNT.name
    )

    # ASSERT
    assert_no_delegations(cli_tester)
