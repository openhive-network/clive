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
from clive_local_tools.data.constants import WATCHED_ACCOUNTS, WORKING_ACCOUNT, WORKING_ACCOUNT_KEY_ALIAS

if TYPE_CHECKING:
    import test_tools as tt

    from clive_local_tools.cli.testing_cli import TestingCli


OTHER_ACCOUNT: Final[tt.Account] = WATCHED_ACCOUNTS[0]
OTHER_ACCOUNT2: Final[tt.Account] = WATCHED_ACCOUNTS[1]
WEIGHT: Final[int] = 213
MODIFIED_WEIGHT: Final[int] = 214
WEIGHT_THRESHOLD: Final[int] = 2


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_chaining(testing_cli: TestingCli, authority: AuthorityType) -> None:
    # ACT
    testing_cli.process_update_authority(
        authority, password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS, threshold=str(WEIGHT_THRESHOLD)
    ).add_account(account=OTHER_ACCOUNT.name, weight=str(WEIGHT)).add_key(
        key=OTHER_ACCOUNT.public_key, weight=str(WEIGHT)
    ).fire()

    # ASSERT
    assert_weight_threshold(testing_cli, authority, WEIGHT_THRESHOLD)
    assert_is_authority(testing_cli, WORKING_ACCOUNT.public_key, authority)
    assert_is_authority(testing_cli, OTHER_ACCOUNT.name, authority)
    assert_is_authority(testing_cli, OTHER_ACCOUNT.public_key, authority)
    assert_authority_weight(testing_cli, OTHER_ACCOUNT.name, authority, WEIGHT)
    assert_authority_weight(testing_cli, OTHER_ACCOUNT.public_key, authority, WEIGHT)


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_chaining2(testing_cli: TestingCli, authority: AuthorityType) -> None:
    # ACT
    testing_cli.process_update_authority(
        authority, password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS, threshold=str(WEIGHT_THRESHOLD)
    ).add_account(account=OTHER_ACCOUNT.name, weight=str(WEIGHT)).add_account(
        account=OTHER_ACCOUNT2.name, weight=str(WEIGHT)
    ).add_key(
        key=OTHER_ACCOUNT.public_key, weight=str(WEIGHT)
    ).remove_key(
        key=WORKING_ACCOUNT.public_key
    ).fire()

    # ASSERT
    assert_weight_threshold(testing_cli, authority, WEIGHT_THRESHOLD)
    assert_is_authority(testing_cli, OTHER_ACCOUNT.name, authority)
    assert_is_authority(testing_cli, OTHER_ACCOUNT2.name, authority)
    assert_is_authority(testing_cli, OTHER_ACCOUNT.public_key, authority)
    assert_authority_weight(testing_cli, OTHER_ACCOUNT2.name, authority, WEIGHT)
    assert_authority_weight(testing_cli, OTHER_ACCOUNT.public_key, authority, WEIGHT)
    assert_is_not_authority(testing_cli, WORKING_ACCOUNT.public_key, authority)


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_chaining3(testing_cli: TestingCli, authority: AuthorityType) -> None:
    # ACT
    testing_cli.process_update_authority(
        authority, password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS, threshold=str(WEIGHT_THRESHOLD)
    ).add_key(key=OTHER_ACCOUNT.public_key, weight=str(WEIGHT)).add_account(
        account=OTHER_ACCOUNT.name, weight=str(WEIGHT)
    ).modify_key(
        key=WORKING_ACCOUNT.public_key, weight=str(MODIFIED_WEIGHT)
    ).fire()

    # ASSERT
    assert_is_authority(testing_cli, WORKING_ACCOUNT.public_key, authority)
    assert_is_authority(testing_cli, OTHER_ACCOUNT.public_key, authority)
    assert_is_authority(testing_cli, OTHER_ACCOUNT.name, authority)
    assert_authority_weight(testing_cli, WORKING_ACCOUNT.public_key, authority, MODIFIED_WEIGHT)
    assert_authority_weight(testing_cli, OTHER_ACCOUNT.public_key, authority, WEIGHT)
    assert_authority_weight(testing_cli, OTHER_ACCOUNT.name, authority, WEIGHT)
