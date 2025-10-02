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
from clive_local_tools.testnet_block_log import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_DATA

if TYPE_CHECKING:
    from pathlib import Path

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
async def test_save_file_before_chaining(
    cli_tester: CLITester, authority: AuthorityLevelRegular, tmp_path: Path
) -> None:
    # ARRANGE
    file_path = tmp_path / f"trx_update_{authority}_authority.json"

    # ACT
    cli_tester.process_update_authority(
        authority,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        threshold=WEIGHT_THRESHOLD,
    ).add_key(
        key=OTHER_ACCOUNT.public_key,
        weight=WEIGHT,
        save_file=file_path,
    ).add_account(
        account=OTHER_ACCOUNT.name,
        weight=WEIGHT,
    ).modify_key(
        key=WORKING_ACCOUNT_DATA.account.public_key,
        weight=MODIFIED_WEIGHT,
        broadcast=False,
    ).fire()

    # ASSERT
    assert file_path.exists(), f"file {file_path} with transaction should be created"
    assert_is_authority(cli_tester, WORKING_ACCOUNT_DATA.account.public_key, authority)
    assert_is_not_authority(cli_tester, OTHER_ACCOUNT.public_key, authority)
    assert_is_not_authority(cli_tester, OTHER_ACCOUNT.name, authority)


@pytest.mark.parametrize("authority", AUTHORITY_LEVELS_REGULAR)
async def test_save_file_option_after_chaining(
    cli_tester: CLITester, authority: AuthorityLevelRegular, tmp_path: Path
) -> None:
    # ARRANGE
    file_path = tmp_path / f"trx_update_{authority}_authority.json"

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
        save_file=file_path,
    ).fire()

    # ASSERT
    assert file_path.exists(), f"file {file_path} with transaction should be created"
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
async def test_save_file_option_multiple_times(
    cli_tester: CLITester, authority: AuthorityLevelRegular, tmp_path: Path
) -> None:
    # ARRANGE
    first_file_path = tmp_path / "notcreated.json"
    second_file_path = tmp_path / f"trx_update_{authority}_authority.json"

    # ACT
    cli_tester.process_update_authority(
        authority,
        save_file=first_file_path,
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
        save_file=second_file_path,
    ).fire()

    # ASSERT
    assert not first_file_path.exists(), f"file {first_file_path} with transaction should not be created"
    assert second_file_path.exists(), f"file {second_file_path} with transaction should be created"
    assert_is_authority(cli_tester, WORKING_ACCOUNT_DATA.account.public_key, authority)
    assert_is_authority(cli_tester, OTHER_ACCOUNT.name, authority)
    assert_is_authority(cli_tester, OTHER_ACCOUNT.public_key, authority)
    assert_authority_weight(cli_tester, OTHER_ACCOUNT.name, authority, WEIGHT)
    assert_authority_weight(cli_tester, OTHER_ACCOUNT.public_key, authority, WEIGHT)
    assert_authority_weight(cli_tester, WORKING_ACCOUNT_DATA.account.public_key, authority, MODIFIED_WEIGHT)
