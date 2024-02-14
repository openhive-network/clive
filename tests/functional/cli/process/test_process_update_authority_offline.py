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
from clive_local_tools.data.constants import (
    WATCHED_ACCOUNTS,
    WORKING_ACCOUNT,
    WORKING_ACCOUNT_KEY_ALIAS,
    WORKING_ACCOUNT_PASSWORD,
)

if TYPE_CHECKING:
    import test_tools as tt

    from clive_local_tools.cli.cli_tester import CLITester


OTHER_ACCOUNT: Final[tt.Account] = WATCHED_ACCOUNTS[0]
WEIGHT_THRESHOLD: Final[int] = 12
WEIGHT: Final[int] = 323
MODIFIED_WEIGHT: Final[int] = 324


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_set_threshold_offline(cli_tester: CLITester, authority: AuthorityType) -> None:
    # ACT
    cli_tester.process_update_authority(
        authority,
        force_offline=True,
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        threshold=WEIGHT_THRESHOLD,
    ).add_account(account=WORKING_ACCOUNT.name, weight=WEIGHT).fire()

    # ASSERT
    assert_weight_threshold(cli_tester, authority, WEIGHT_THRESHOLD)
    assert_is_authority(cli_tester, WORKING_ACCOUNT.name, authority)
    assert_authority_weight(cli_tester, WORKING_ACCOUNT.name, authority, WEIGHT)


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_add_account_offline(cli_tester: CLITester, authority: AuthorityType) -> None:
    # ACT
    cli_tester.process_update_authority(
        authority, force_offline=True, password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS
    ).add_account(account=OTHER_ACCOUNT.name, weight=WEIGHT).fire()

    # ASSERT
    assert_is_authority(cli_tester, OTHER_ACCOUNT.name, authority)
    assert_authority_weight(cli_tester, OTHER_ACCOUNT.name, authority, WEIGHT)
    assert_is_not_authority(cli_tester, WORKING_ACCOUNT.name, authority)
    assert_is_not_authority(cli_tester, WORKING_ACCOUNT.public_key, authority)


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_modify_key_offline(cli_tester: CLITester, authority: AuthorityType) -> None:
    # ACT
    cli_tester.process_update_authority(
        authority, force_offline=True, password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS
    ).add_key(key=WORKING_ACCOUNT.public_key, weight=WEIGHT).modify_key(
        key=WORKING_ACCOUNT.public_key, weight=MODIFIED_WEIGHT
    ).fire()

    # ASSERT
    assert_is_authority(cli_tester, WORKING_ACCOUNT.public_key, authority)
    assert_authority_weight(cli_tester, WORKING_ACCOUNT.public_key, authority, MODIFIED_WEIGHT)
