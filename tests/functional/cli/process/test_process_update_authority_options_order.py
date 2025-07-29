from __future__ import annotations

from typing import TYPE_CHECKING, Final, get_args

import pytest

from clive.__private.cli.commands.process.process_account_update import OptionAlreadySetError
from clive.__private.cli.types import AuthorityType
from clive_local_tools.cli.checkers import (
    assert_authority_weight,
    assert_is_authority,
    assert_is_not_authority,
    assert_weight_threshold,
)
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.testnet_block_log import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_DATA

if TYPE_CHECKING:
    from pathlib import Path

    import test_tools as tt

    from clive_local_tools.cli.cli_tester import CLITester


OTHER_ACCOUNT: Final[tt.Account] = WATCHED_ACCOUNTS_DATA[0].account
OTHER_ACCOUNT2: Final[tt.Account] = WATCHED_ACCOUNTS_DATA[1].account
WEIGHT: Final[int] = 213
MODIFIED_WEIGHT: Final[int] = 214
WEIGHT_THRESHOLD: Final[int] = 2


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_sign_before_chaining(cli_tester: CLITester, authority: AuthorityType) -> None:
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


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_sign_after_chaining(cli_tester: CLITester, authority: AuthorityType) -> None:
    # ACT
    cli_tester.process_update_authority(authority, threshold=WEIGHT_THRESHOLD).add_key(
        key=OTHER_ACCOUNT.public_key, weight=WEIGHT
    ).add_account(account=OTHER_ACCOUNT.name, weight=WEIGHT).modify_key(
        key=WORKING_ACCOUNT_DATA.account.public_key, weight=MODIFIED_WEIGHT, sign=WORKING_ACCOUNT_KEY_ALIAS
    ).fire()

    # ASSERT
    assert_is_authority(cli_tester, WORKING_ACCOUNT_DATA.account.public_key, authority)
    assert_is_authority(cli_tester, OTHER_ACCOUNT.public_key, authority)
    assert_is_authority(cli_tester, OTHER_ACCOUNT.name, authority)
    assert_authority_weight(cli_tester, WORKING_ACCOUNT_DATA.account.public_key, authority, MODIFIED_WEIGHT)
    assert_authority_weight(cli_tester, OTHER_ACCOUNT.public_key, authority, WEIGHT)
    assert_authority_weight(cli_tester, OTHER_ACCOUNT.name, authority, WEIGHT)


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_save_file_before_chaining(cli_tester: CLITester, authority: AuthorityType, tmp_path: Path) -> None:
    # ARRANGE
    file_path = tmp_path / f"trx_update_{authority}_authority.json"

    # ACT
    cli_tester.process_update_authority(authority, sign=WORKING_ACCOUNT_KEY_ALIAS, threshold=WEIGHT_THRESHOLD).add_key(
        key=OTHER_ACCOUNT.public_key, weight=WEIGHT, save_file=file_path
    ).add_account(account=OTHER_ACCOUNT.name, weight=WEIGHT).modify_key(
        key=WORKING_ACCOUNT_DATA.account.public_key, weight=MODIFIED_WEIGHT, broadcast=False
    ).fire()

    # ASSERT
    assert file_path.exists(), f"file {file_path} with transaction should be created"
    assert_is_authority(cli_tester, WORKING_ACCOUNT_DATA.account.public_key, authority)
    assert_is_not_authority(cli_tester, OTHER_ACCOUNT.public_key, authority)
    assert_is_not_authority(cli_tester, OTHER_ACCOUNT.name, authority)


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_save_file_option_after_chaining(cli_tester: CLITester, authority: AuthorityType, tmp_path: Path) -> None:
    # ARRANGE
    file_path = tmp_path / f"trx_update_{authority}_authority.json"

    # ACT
    cli_tester.process_update_authority(authority, sign=WORKING_ACCOUNT_KEY_ALIAS, threshold=WEIGHT_THRESHOLD).add_key(
        key=OTHER_ACCOUNT.public_key, weight=WEIGHT
    ).add_account(account=OTHER_ACCOUNT.name, weight=WEIGHT).modify_key(
        key=WORKING_ACCOUNT_DATA.account.public_key, weight=MODIFIED_WEIGHT, broadcast=False, save_file=file_path
    ).fire()

    # ASSERT
    assert file_path.exists(), f"file {file_path} with transaction should be created"
    assert_is_authority(cli_tester, WORKING_ACCOUNT_DATA.account.public_key, authority)
    assert_is_not_authority(cli_tester, OTHER_ACCOUNT.public_key, authority)
    assert_is_not_authority(cli_tester, OTHER_ACCOUNT.name, authority)


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_no_broadcast_before_chaining(cli_tester: CLITester, authority: AuthorityType) -> None:
    # ACT
    cli_tester.process_update_authority(
        authority, sign=WORKING_ACCOUNT_KEY_ALIAS, threshold=WEIGHT_THRESHOLD, broadcast=False
    ).add_account(account=OTHER_ACCOUNT.name, weight=WEIGHT).add_key(key=OTHER_ACCOUNT.public_key, weight=WEIGHT).fire()

    # ASSERT
    assert_is_authority(cli_tester, WORKING_ACCOUNT_DATA.account.public_key, authority)
    assert_is_not_authority(cli_tester, OTHER_ACCOUNT.public_key, authority)
    assert_is_not_authority(cli_tester, OTHER_ACCOUNT.name, authority)


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_no_broadcast_overriden(cli_tester: CLITester, authority: AuthorityType) -> None:
    # ACT
    cli_tester.process_update_authority(
        authority, sign=WORKING_ACCOUNT_KEY_ALIAS, threshold=WEIGHT_THRESHOLD, broadcast=False
    ).add_account(account=OTHER_ACCOUNT.name, weight=WEIGHT).add_key(
        key=OTHER_ACCOUNT.public_key, weight=WEIGHT, broadcast=True
    ).fire()

    # ASSERT
    assert_weight_threshold(cli_tester, authority, WEIGHT_THRESHOLD)
    assert_is_authority(cli_tester, WORKING_ACCOUNT_DATA.account.public_key, authority)
    assert_is_authority(cli_tester, OTHER_ACCOUNT.name, authority)
    assert_is_authority(cli_tester, OTHER_ACCOUNT.public_key, authority)
    assert_authority_weight(cli_tester, OTHER_ACCOUNT.name, authority, WEIGHT)
    assert_authority_weight(cli_tester, OTHER_ACCOUNT.public_key, authority, WEIGHT)


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_negative_sign_option_multiple_times(cli_tester: CLITester, authority: AuthorityType) -> None:
    # ARRANGE
    expected_error_message = str(OptionAlreadySetError("sign"))

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=expected_error_message):
        cli_tester.process_update_authority(
            authority, sign=WORKING_ACCOUNT_KEY_ALIAS, threshold=WEIGHT_THRESHOLD
        ).add_key(key=OTHER_ACCOUNT.public_key, weight=WEIGHT).add_account(
            account=OTHER_ACCOUNT.name, weight=WEIGHT
        ).modify_key(
            key=WORKING_ACCOUNT_DATA.account.public_key, weight=MODIFIED_WEIGHT, sign=WORKING_ACCOUNT_KEY_ALIAS
        ).fire()


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_negative_save_file_option_multiple_times(
    cli_tester: CLITester, authority: AuthorityType, tmp_path: Path
) -> None:
    # ARRANGE
    file_path = tmp_path / f"trx_update_{authority}_authority.json"
    expected_error_message = str(OptionAlreadySetError("save-file"))

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=expected_error_message):
        cli_tester.process_update_authority(authority, save_file=file_path, threshold=WEIGHT_THRESHOLD).add_key(
            key=OTHER_ACCOUNT.public_key, weight=WEIGHT
        ).add_account(account=OTHER_ACCOUNT.name, weight=WEIGHT).modify_key(
            key=WORKING_ACCOUNT_DATA.account.public_key, weight=MODIFIED_WEIGHT, save_file=file_path
        ).fire()
