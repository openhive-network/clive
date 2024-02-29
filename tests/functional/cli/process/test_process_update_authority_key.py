from __future__ import annotations

from typing import TYPE_CHECKING, Final, get_args

import pytest

from clive.__private.cli.types import AuthorityType
from clive_local_tools.cli.checkers import assert_authority_weight, assert_is_authority, assert_is_not_authority
from clive_local_tools.data.constants import WATCHED_ACCOUNTS, WORKING_ACCOUNT, WORKING_ACCOUNT_KEY_ALIAS

if TYPE_CHECKING:
    import test_tools as tt

    from clive_local_tools.cli.testing_cli import TestingCli


OTHER_ACCOUNT: Final[tt.Account] = WATCHED_ACCOUNTS[0]
WEIGHT: Final[int] = 123
MODIFIED_WEIGHT: Final[int] = 124


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_add_key(testing_cli: TestingCli, authority: AuthorityType) -> None:
    # ACT
    testing_cli.process_update_authority(
        authority, password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS
    ).add_key(key=OTHER_ACCOUNT.public_key, weight=WEIGHT).fire()

    # ASSERT
    assert_is_authority(testing_cli, OTHER_ACCOUNT.public_key, authority)
    assert_authority_weight(testing_cli, OTHER_ACCOUNT.public_key, authority, WEIGHT)


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_remove_key(testing_cli: TestingCli, authority: AuthorityType) -> None:
    # ARRANGE
    testing_cli.process_update_authority(
        authority, password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS
    ).add_key(key=OTHER_ACCOUNT.public_key, weight=WEIGHT).fire()
    assert_is_authority(testing_cli, OTHER_ACCOUNT.public_key, authority)

    # ACT
    testing_cli.process_update_authority(
        authority, password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS
    ).remove_key(key=OTHER_ACCOUNT.public_key).fire()

    # ASSERT
    assert_is_not_authority(testing_cli, OTHER_ACCOUNT.public_key, authority)


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_modify_key(testing_cli: TestingCli, authority: AuthorityType) -> None:
    # ARRANGE
    testing_cli.process_update_authority(
        authority, password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS
    ).add_key(key=OTHER_ACCOUNT.public_key, weight=WEIGHT).fire()
    assert_is_authority(testing_cli, OTHER_ACCOUNT.public_key, authority)

    # ACT
    testing_cli.process_update_authority(
        authority, password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS
    ).modify_key(key=OTHER_ACCOUNT.public_key, weight=MODIFIED_WEIGHT).fire()

    # ASSERT
    assert_is_authority(testing_cli, OTHER_ACCOUNT.public_key, authority)
    assert_authority_weight(testing_cli, OTHER_ACCOUNT.public_key, authority, MODIFIED_WEIGHT)
