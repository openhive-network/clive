from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive.__private.settings import safe_settings
from clive_local_tools.cli.checkers import assert_no_exit_code_error
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.storage_migration.helpers import BLANK_PROFILES, copy_blank_profile_files

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


@pytest.fixture(autouse=True)
def _prepare_profile_files() -> None:
    copy_blank_profile_files(safe_settings.data_path)


async def test_show_profiles_includes_all_valid_versions(cli_tester_locked: CLITester) -> None:
    # ACT & ASSERT
    result = cli_tester_locked.show_profiles()
    assert_no_exit_code_error(result)
    for profile_name in BLANK_PROFILES:
        assert profile_name in result.output, f"Profile {profile_name} should be listed"


async def test_remove_profile_force_not_required(cli_tester_locked: CLITester) -> None:
    # ARRANGE
    profile_name = "three"

    # ACT
    cli_tester_locked.configure_profile_delete(profile_name=profile_name)

    # ASSERT
    result = cli_tester_locked.show_profiles()
    assert profile_name not in result.output, f"Profile {profile_name} should be deleted"


async def test_remove_profile_with_force(cli_tester_locked: CLITester) -> None:
    # ARRANGE
    profile_name = "one"

    # ACT
    cli_tester_locked.configure_profile_delete(profile_name=profile_name, force=True)

    # ASSERT
    result = cli_tester_locked.show_profiles()
    assert profile_name not in result.output, f"Profile {profile_name} should be deleted"


async def test_try_remove_profile_without_force(cli_tester_locked: CLITester) -> None:
    # ARRANGE
    profile_name = "one"
    message = (
        f"Multiple versions or backups of profile `{profile_name}` exist."
        " If you want to remove all, please use the '--force' option."
    )

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester_locked.configure_profile_delete(profile_name=profile_name)


@pytest.mark.parametrize("force", [True, False])
async def test_remove_non_existing_profile(cli_tester_locked: CLITester, *, force: bool) -> None:
    # ARRANGE
    profile_name = "non-existing"
    message = f"Profile `{profile_name}` does not exist."

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester_locked.configure_profile_delete(profile_name=profile_name, force=force)
