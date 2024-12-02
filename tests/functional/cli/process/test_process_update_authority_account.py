from __future__ import annotations

from typing import TYPE_CHECKING, Final, get_args

import pytest

from clive.__private.cli.types import AuthorityType
from clive_local_tools.cli.checkers import assert_authority_weight, assert_is_authority, assert_is_not_authority
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.testnet_block_log import WATCHED_ACCOUNTS_DATA

if TYPE_CHECKING:
    import test_tools as tt

    from clive_local_tools.cli.cli_tester import CLITester


OTHER_ACCOUNT: Final[tt.Account] = WATCHED_ACCOUNTS_DATA[0].account
WEIGHT: Final[int] = 123
MODIFIED_WEIGHT: Final[int] = 124


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_add_account(cli_tester: CLITester, authority: AuthorityType) -> None:
    # ACT
    cli_tester.process_update_authority(authority, sign=WORKING_ACCOUNT_KEY_ALIAS).add_account(
        account=OTHER_ACCOUNT.name, weight=WEIGHT
    ).fire()

    # ASSERT
    assert_is_authority(cli_tester, OTHER_ACCOUNT.name, authority)
    assert_authority_weight(cli_tester, OTHER_ACCOUNT.name, authority, WEIGHT)


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_remove_account(cli_tester: CLITester, authority: AuthorityType) -> None:
    # ARRANGE
    cli_tester.process_update_authority(authority, sign=WORKING_ACCOUNT_KEY_ALIAS).add_account(
        account=OTHER_ACCOUNT.name, weight=WEIGHT
    ).fire()
    assert_is_authority(cli_tester, OTHER_ACCOUNT.name, authority)

    # ACT
    cli_tester.process_update_authority(authority, sign=WORKING_ACCOUNT_KEY_ALIAS).remove_account(
        account=OTHER_ACCOUNT.name
    ).fire()

    # ASSERT
    assert_is_not_authority(cli_tester, OTHER_ACCOUNT.name, authority)


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_modify_account(cli_tester: CLITester, authority: AuthorityType) -> None:
    # ARRANGE
    cli_tester.process_update_authority(authority, sign=WORKING_ACCOUNT_KEY_ALIAS).add_account(
        account=OTHER_ACCOUNT.name, weight=WEIGHT
    ).fire()
    assert_is_authority(cli_tester, OTHER_ACCOUNT.name, authority)

    # ACT
    cli_tester.process_update_authority(authority, sign=WORKING_ACCOUNT_KEY_ALIAS).modify_account(
        account=OTHER_ACCOUNT.name, weight=MODIFIED_WEIGHT
    ).fire()

    # ASSERT
    assert_is_authority(cli_tester, OTHER_ACCOUNT.name, authority)
    assert_authority_weight(cli_tester, OTHER_ACCOUNT.name, authority, MODIFIED_WEIGHT)
