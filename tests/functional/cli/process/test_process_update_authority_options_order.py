from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.core.constants.authority import AUTHORITY_LEVELS_REGULAR
from clive_local_tools.cli.checkers import (
    assert_authority_weight,
    assert_is_authority,
    assert_is_not_authority,
    assert_weight_threshold,
)
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.helpers import create_transaction_filepath
from clive_local_tools.testnet_block_log import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_DATA

if TYPE_CHECKING:
    import test_tools as tt

    from clive.__private.core.types import AuthorityLevelRegular
    from clive_local_tools.cli.cli_tester import CLITester


OTHER_ACCOUNT: Final[tt.Account] = WATCHED_ACCOUNTS_DATA[0].account
OTHER_ACCOUNT2: Final[tt.Account] = WATCHED_ACCOUNTS_DATA[1].account
WEIGHT: Final[int] = 213
MODIFIED_WEIGHT: Final[int] = 214
WEIGHT_THRESHOLD: Final[int] = 2


@pytest.mark.parametrize("authority", AUTHORITY_LEVELS_REGULAR)
async def test_sign_before_chaining(cli_tester: CLITester, authority: AuthorityLevelRegular) -> None:
    # ACT
    cli_tester.process_update_authority(
        authority,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        threshold=WEIGHT_THRESHOLD,
    ).add_key(
        key=OTHER_ACCOUNT.public_key,
        weight=WEIGHT,
    ).add_account(
        account=OTHER_ACCOUNT.name,
        weight=WEIGHT,
    ).modify_key(
        key=WORKING_ACCOUNT_DATA.account.public_key,
        weight=MODIFIED_WEIGHT,
    ).fire()

    # ASSERT
    assert_is_authority(cli_tester, WORKING_ACCOUNT_DATA.account.public_key, authority)
    assert_is_authority(cli_tester, OTHER_ACCOUNT.public_key, authority)
    assert_is_authority(cli_tester, OTHER_ACCOUNT.name, authority)
    assert_authority_weight(cli_tester, WORKING_ACCOUNT_DATA.account.public_key, authority, MODIFIED_WEIGHT)
    assert_authority_weight(cli_tester, OTHER_ACCOUNT.public_key, authority, WEIGHT)
    assert_authority_weight(cli_tester, OTHER_ACCOUNT.name, authority, WEIGHT)


@pytest.mark.parametrize("authority", AUTHORITY_LEVELS_REGULAR)
async def test_sign_after_chaining(cli_tester: CLITester, authority: AuthorityLevelRegular) -> None:
    # ACT
    cli_tester.process_update_authority(
        authority,
        threshold=WEIGHT_THRESHOLD,
    ).add_key(
        key=OTHER_ACCOUNT.public_key,
        weight=WEIGHT,
    ).add_account(
        account=OTHER_ACCOUNT.name,
        weight=WEIGHT,
    ).modify_key(
        key=WORKING_ACCOUNT_DATA.account.public_key,
        weight=MODIFIED_WEIGHT,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    ).fire()

    # ASSERT
    assert_is_authority(cli_tester, WORKING_ACCOUNT_DATA.account.public_key, authority)
    assert_is_authority(cli_tester, OTHER_ACCOUNT.public_key, authority)
    assert_is_authority(cli_tester, OTHER_ACCOUNT.name, authority)
    assert_authority_weight(cli_tester, WORKING_ACCOUNT_DATA.account.public_key, authority, MODIFIED_WEIGHT)
    assert_authority_weight(cli_tester, OTHER_ACCOUNT.public_key, authority, WEIGHT)
    assert_authority_weight(cli_tester, OTHER_ACCOUNT.name, authority, WEIGHT)


@pytest.mark.parametrize("authority", AUTHORITY_LEVELS_REGULAR)
async def test_save_file_before_chaining(cli_tester: CLITester, authority: AuthorityLevelRegular) -> None:
    # ARRANGE
    transaction_filepath = create_transaction_filepath()

    # ACT
    cli_tester.process_update_authority(
        authority,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        threshold=WEIGHT_THRESHOLD,
    ).add_key(
        key=OTHER_ACCOUNT.public_key,
        weight=WEIGHT,
        save_file=transaction_filepath,
    ).add_account(
        account=OTHER_ACCOUNT.name,
        weight=WEIGHT,
    ).modify_key(
        key=WORKING_ACCOUNT_DATA.account.public_key,
        weight=MODIFIED_WEIGHT,
        broadcast=False,
    ).fire()

    # ASSERT
    assert transaction_filepath.exists(), f"file {transaction_filepath} with transaction should be created"
    assert_is_authority(cli_tester, WORKING_ACCOUNT_DATA.account.public_key, authority)
    assert_is_not_authority(cli_tester, OTHER_ACCOUNT.public_key, authority)
    assert_is_not_authority(cli_tester, OTHER_ACCOUNT.name, authority)


@pytest.mark.parametrize("authority", AUTHORITY_LEVELS_REGULAR)
async def test_save_file_option_after_chaining(cli_tester: CLITester, authority: AuthorityLevelRegular) -> None:
    # ARRANGE
    transaction_filepath = create_transaction_filepath()

    # ACT
    cli_tester.process_update_authority(
        authority,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        threshold=WEIGHT_THRESHOLD,
    ).add_key(
        key=OTHER_ACCOUNT.public_key,
        weight=WEIGHT,
    ).add_account(
        account=OTHER_ACCOUNT.name,
        weight=WEIGHT,
    ).modify_key(
        key=WORKING_ACCOUNT_DATA.account.public_key,
        weight=MODIFIED_WEIGHT,
        broadcast=False,
        save_file=transaction_filepath,
    ).fire()

    # ASSERT
    assert transaction_filepath.exists(), f"file {transaction_filepath} with transaction should be created"
    assert_is_authority(cli_tester, WORKING_ACCOUNT_DATA.account.public_key, authority)
    assert_is_not_authority(cli_tester, OTHER_ACCOUNT.public_key, authority)
    assert_is_not_authority(cli_tester, OTHER_ACCOUNT.name, authority)


@pytest.mark.parametrize("authority", AUTHORITY_LEVELS_REGULAR)
async def test_no_broadcast_before_chaining(cli_tester: CLITester, authority: AuthorityLevelRegular) -> None:
    # ACT
    cli_tester.process_update_authority(
        authority,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        threshold=WEIGHT_THRESHOLD,
        broadcast=False,
    ).add_account(
        account=OTHER_ACCOUNT.name,
        weight=WEIGHT,
    ).add_key(
        key=OTHER_ACCOUNT.public_key,
        weight=WEIGHT,
    ).fire()

    # ASSERT
    assert_is_authority(cli_tester, WORKING_ACCOUNT_DATA.account.public_key, authority)
    assert_is_not_authority(cli_tester, OTHER_ACCOUNT.public_key, authority)
    assert_is_not_authority(cli_tester, OTHER_ACCOUNT.name, authority)


@pytest.mark.parametrize("authority", AUTHORITY_LEVELS_REGULAR)
async def test_no_broadcast_overriden(cli_tester: CLITester, authority: AuthorityLevelRegular) -> None:
    # ACT
    cli_tester.process_update_authority(
        authority,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        threshold=WEIGHT_THRESHOLD,
        broadcast=False,
    ).add_account(
        account=OTHER_ACCOUNT.name,
        weight=WEIGHT,
    ).add_key(
        key=OTHER_ACCOUNT.public_key,
        weight=WEIGHT,
        broadcast=True,
    ).fire()

    # ASSERT
    assert_weight_threshold(cli_tester, authority, WEIGHT_THRESHOLD)
    assert_is_authority(cli_tester, WORKING_ACCOUNT_DATA.account.public_key, authority)
    assert_is_authority(cli_tester, OTHER_ACCOUNT.name, authority)
    assert_is_authority(cli_tester, OTHER_ACCOUNT.public_key, authority)
    assert_authority_weight(cli_tester, OTHER_ACCOUNT.name, authority, WEIGHT)
    assert_authority_weight(cli_tester, OTHER_ACCOUNT.public_key, authority, WEIGHT)


@pytest.mark.parametrize("authority", AUTHORITY_LEVELS_REGULAR)
async def test_sign_option_multiple_times(cli_tester: CLITester, authority: AuthorityLevelRegular) -> None:
    # ACT
    cli_tester.process_update_authority(
        authority,
        sign_with="nonexisting",
        threshold=WEIGHT_THRESHOLD,
    ).add_key(
        key=OTHER_ACCOUNT.public_key,
        weight=WEIGHT,
    ).add_account(
        account=OTHER_ACCOUNT.name,
        weight=WEIGHT,
    ).modify_key(
        key=WORKING_ACCOUNT_DATA.account.public_key,
        weight=MODIFIED_WEIGHT,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    ).fire()

    # ASSERT
    assert_is_authority(cli_tester, WORKING_ACCOUNT_DATA.account.public_key, authority)
    assert_is_authority(cli_tester, OTHER_ACCOUNT.name, authority)
    assert_is_authority(cli_tester, OTHER_ACCOUNT.public_key, authority)
    assert_authority_weight(cli_tester, OTHER_ACCOUNT.name, authority, WEIGHT)
    assert_authority_weight(cli_tester, OTHER_ACCOUNT.public_key, authority, WEIGHT)
    assert_authority_weight(cli_tester, WORKING_ACCOUNT_DATA.account.public_key, authority, MODIFIED_WEIGHT)


@pytest.mark.parametrize("authority", AUTHORITY_LEVELS_REGULAR)
async def test_save_file_option_multiple_times(cli_tester: CLITester, authority: AuthorityLevelRegular) -> None:
    # ARRANGE
    not_created_transaction_filepath = create_transaction_filepath("not_created")
    created_transaction_filepath = create_transaction_filepath("created")

    # ACT
    cli_tester.process_update_authority(
        authority,
        save_file=not_created_transaction_filepath,
        threshold=WEIGHT_THRESHOLD,
    ).add_key(
        key=OTHER_ACCOUNT.public_key,
        weight=WEIGHT,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    ).add_account(
        account=OTHER_ACCOUNT.name,
        weight=WEIGHT,
    ).modify_key(
        key=WORKING_ACCOUNT_DATA.account.public_key,
        weight=MODIFIED_WEIGHT,
        save_file=created_transaction_filepath,
    ).fire()

    # ASSERT
    assert not not_created_transaction_filepath.exists(), (
        f"file {not_created_transaction_filepath} with transaction should not be created"
    )
    assert created_transaction_filepath.exists(), (
        f"file {created_transaction_filepath} with transaction should be created"
    )
    assert_is_authority(cli_tester, WORKING_ACCOUNT_DATA.account.public_key, authority)
    assert_is_authority(cli_tester, OTHER_ACCOUNT.name, authority)
    assert_is_authority(cli_tester, OTHER_ACCOUNT.public_key, authority)
    assert_authority_weight(cli_tester, OTHER_ACCOUNT.name, authority, WEIGHT)
    assert_authority_weight(cli_tester, OTHER_ACCOUNT.public_key, authority, WEIGHT)
    assert_authority_weight(cli_tester, WORKING_ACCOUNT_DATA.account.public_key, authority, MODIFIED_WEIGHT)
