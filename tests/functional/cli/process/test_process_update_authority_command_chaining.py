from __future__ import annotations

from typing import TYPE_CHECKING, Final, get_args

import pytest

from clive.__private.cli.types import AuthorityType
from clive_local_tools.cli.checkers import (
    assert_authority_weight,
    assert_is_authority,
    assert_is_not_authority,
    assert_weight_threshold,
)
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.testnet_block_log import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_DATA

if TYPE_CHECKING:
    import test_tools as tt

    from clive_local_tools.cli.cli_tester import CLITester


OTHER_ACCOUNT: Final[tt.Account] = WATCHED_ACCOUNTS_DATA[0].account
OTHER_ACCOUNT2: Final[tt.Account] = WATCHED_ACCOUNTS_DATA[1].account
WEIGHT: Final[int] = 213
MODIFIED_WEIGHT: Final[int] = 214
WEIGHT_THRESHOLD: Final[int] = 2


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_chaining(cli_tester: CLITester, authority: AuthorityType) -> None:
    # ACT
    cli_tester.process_update_authority(
        authority, sign=WORKING_ACCOUNT_KEY_ALIAS, threshold=WEIGHT_THRESHOLD
    ).add_account(account=OTHER_ACCOUNT.name, weight=WEIGHT).add_key(key=OTHER_ACCOUNT.public_key, weight=WEIGHT).fire()

    # ASSERT
    assert_weight_threshold(cli_tester, authority, WEIGHT_THRESHOLD)
    assert_is_authority(cli_tester, WORKING_ACCOUNT_DATA.account.public_key, authority)
    assert_is_authority(cli_tester, OTHER_ACCOUNT.name, authority)
    assert_is_authority(cli_tester, OTHER_ACCOUNT.public_key, authority)
    assert_authority_weight(cli_tester, OTHER_ACCOUNT.name, authority, WEIGHT)
    assert_authority_weight(cli_tester, OTHER_ACCOUNT.public_key, authority, WEIGHT)


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_chaining2(cli_tester: CLITester, authority: AuthorityType) -> None:
    # ACT
    cli_tester.process_update_authority(
        authority, sign=WORKING_ACCOUNT_KEY_ALIAS, threshold=WEIGHT_THRESHOLD
    ).add_account(account=OTHER_ACCOUNT.name, weight=WEIGHT).add_account(
        account=OTHER_ACCOUNT2.name, weight=WEIGHT
    ).add_key(key=OTHER_ACCOUNT.public_key, weight=WEIGHT).remove_key(
        key=WORKING_ACCOUNT_DATA.account.public_key
    ).fire()

    # ASSERT
    assert_weight_threshold(cli_tester, authority, WEIGHT_THRESHOLD)
    assert_is_authority(cli_tester, OTHER_ACCOUNT.name, authority)
    assert_is_authority(cli_tester, OTHER_ACCOUNT2.name, authority)
    assert_is_authority(cli_tester, OTHER_ACCOUNT.public_key, authority)
    assert_authority_weight(cli_tester, OTHER_ACCOUNT2.name, authority, WEIGHT)
    assert_authority_weight(cli_tester, OTHER_ACCOUNT.public_key, authority, WEIGHT)
    assert_is_not_authority(cli_tester, WORKING_ACCOUNT_DATA.account.public_key, authority)


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_chaining3(cli_tester: CLITester, authority: AuthorityType) -> None:
    # ACT
    cli_tester.process_update_authority(authority, sign=WORKING_ACCOUNT_KEY_ALIAS, threshold=WEIGHT_THRESHOLD).add_key(
        key=OTHER_ACCOUNT.public_key, weight=WEIGHT
    ).add_account(account=OTHER_ACCOUNT.name, weight=WEIGHT).modify_key(
        key=WORKING_ACCOUNT_DATA.account.public_key, weight=MODIFIED_WEIGHT
    ).fire()

    # ASSERT
    assert_is_authority(cli_tester, WORKING_ACCOUNT_DATA.account.public_key, authority)
    assert_is_authority(cli_tester, OTHER_ACCOUNT.public_key, authority)
    assert_is_authority(cli_tester, OTHER_ACCOUNT.name, authority)
    assert_authority_weight(cli_tester, WORKING_ACCOUNT_DATA.account.public_key, authority, MODIFIED_WEIGHT)
    assert_authority_weight(cli_tester, OTHER_ACCOUNT.public_key, authority, WEIGHT)
    assert_authority_weight(cli_tester, OTHER_ACCOUNT.name, authority, WEIGHT)
