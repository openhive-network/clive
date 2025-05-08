from __future__ import annotations

from typing import Final

import pytest

from clive.__private.settings import safe_settings
from clive.__private.storage.service import (
    MultipleProfileVersionsError,
    PersistentStorageService,
    ProfileDoesNotExistsError,
)
from clive_local_tools.storage_migration import (
    FUTURE_NOT_SUPPORTED_YET_VERSION,
    LEGACY_BACKUP,
    LEGACY_PROFILE,
    VERSIONED_BACKUP,
    VERSIONED_PROFILE,
    VERSIONED_PROFILE_AND_OLDER_BACKUP,
    copy_blank_profile_files,
)


@pytest.fixture(autouse=True)
def _copy_blank_profile_files() -> None:
    copy_blank_profile_files(safe_settings.data_path)


def backup_files_exists(profile_name: str) -> bool:
    """Check if the backup file for the given profile exists."""
    legacy_backup_file = (
        PersistentStorageService._get_legacy_profile_directory()
        / f"{profile_name}{PersistentStorageService.BACKUP_FILENAME_SUFFIX}"
    )
    profile_directory = PersistentStorageService.get_profile_directory(profile_name)
    profile_backup_files = profile_directory.glob(f"*{PersistentStorageService.BACKUP_FILENAME_SUFFIX}")
    return legacy_backup_file.exists() or any(profile_backup_files)


@pytest.mark.parametrize("profile_name", [VERSIONED_PROFILE, FUTURE_NOT_SUPPORTED_YET_VERSION, LEGACY_PROFILE])
def test_delete_profile(profile_name: str) -> None:
    # ARRANGE & ACT
    PersistentStorageService.delete_profile(profile_name)

    # ASSERT
    actual_profiles = PersistentStorageService.list_stored_profile_names()
    assert profile_name not in actual_profiles, f"Profile `{profile_name}` deletion should be successful"


def test_delete_profile_fail_when_backups_exists() -> None:
    # ARRANGE
    profile_name = VERSIONED_PROFILE_AND_OLDER_BACKUP
    message: Final[str] = f"Multiple versions or backups of profile `{profile_name}` exist."

    # ACT
    with pytest.raises(MultipleProfileVersionsError, match=message):
        PersistentStorageService.delete_profile(profile_name)

    # ASSERT
    actual_profiles = PersistentStorageService.list_stored_profile_names()
    assert profile_name in actual_profiles, f"Profile `{profile_name}` deletion should fail"

    assert backup_files_exists(profile_name), f"Backup files for profile `{profile_name}` should be not deleted"


@pytest.mark.parametrize("profile_name", [VERSIONED_BACKUP, LEGACY_BACKUP])
def test_delete_profile_fail_when_only_backup_exists(profile_name: str) -> None:
    # ARRANGE
    message: Final[str] = f"Profile `{profile_name}` does not exist."

    # ACT
    with pytest.raises(ProfileDoesNotExistsError, match=message):
        PersistentStorageService.delete_profile(profile_name)

    # ASSERT
    assert backup_files_exists(profile_name), f"Backup files for profile `{profile_name}` should be not deleted"


@pytest.mark.parametrize("profile_name", [VERSIONED_PROFILE_AND_OLDER_BACKUP, VERSIONED_BACKUP, LEGACY_BACKUP])
def test_force_delete_profile_deletes_backup_files(profile_name: str) -> None:
    # ACT
    PersistentStorageService.delete_profile(profile_name, force=True)

    # ASSERT
    actual_profiles = PersistentStorageService.list_stored_profile_names()
    assert profile_name not in actual_profiles, f"Profile `{profile_name}` deletion should be successful"

    assert not backup_files_exists(profile_name), f"Backup files for profile `{profile_name}` should be also deleted"
