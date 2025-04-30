from __future__ import annotations

from typing import Final

import pytest

from clive.__private.settings import safe_settings
from clive.__private.storage.service import (
    MultipleProfileVersionsError,
    PersistentStorageService,
    ProfileDoesNotExistsError,
)
from clive_local_tools.storage_migration.helpers import copy_blank_profile_files

PROFILE_AND_BACKUP_EXIST: Final[str] = "mary"
ONLY_BACKUP_EXIST: Final[str] = "four"
ONLY_LEGACY_BACKUP_EXIST: Final[str] = "six"


def backup_files_exists(profile_name: str) -> bool:
    """Check if the backup file for the given profile exists."""
    legacy_backup_file = (
        PersistentStorageService._get_legacy_profile_directory()
        / f"{profile_name}{PersistentStorageService.BACKUP_FILENAME_SUFFIX}"
    )
    profile_directory = PersistentStorageService.get_profile_directory(profile_name)
    profile_backup_files = profile_directory.glob(f"*{PersistentStorageService.BACKUP_FILENAME_SUFFIX}")
    return legacy_backup_file.exists() or any(profile_backup_files)


def test_delete_profile_fail_when_backups_exists() -> None:
    # ARRANGE
    copy_blank_profile_files(safe_settings.data_path)
    message: Final[str] = f"Multiple versions or backups of profile `{PROFILE_AND_BACKUP_EXIST}` exist."

    # ACT
    with pytest.raises(MultipleProfileVersionsError, match=message):
        PersistentStorageService.delete_profile(PROFILE_AND_BACKUP_EXIST)

    # ASSERT
    actual_profiles = PersistentStorageService.list_stored_profile_names()
    assert PROFILE_AND_BACKUP_EXIST in actual_profiles, f"Profile `{PROFILE_AND_BACKUP_EXIST}` deletion should fail"

    assert backup_files_exists(PROFILE_AND_BACKUP_EXIST), (
        f"Backup files for profile `{PROFILE_AND_BACKUP_EXIST}` should be not deleted"
    )


@pytest.mark.parametrize("profile_name", [ONLY_BACKUP_EXIST, ONLY_LEGACY_BACKUP_EXIST])
def test_delete_profile_fail_when_only_backup_exists(profile_name: str) -> None:
    # ARRANGE
    copy_blank_profile_files(safe_settings.data_path)
    message: Final[str] = f"Profile `{profile_name}` does not exist."

    # ACT
    with pytest.raises(ProfileDoesNotExistsError, match=message):
        PersistentStorageService.delete_profile(profile_name)

    # ASSERT
    assert backup_files_exists(profile_name), f"Backup files for profile `{profile_name}` should be not deleted"


@pytest.mark.parametrize("profile_name", [PROFILE_AND_BACKUP_EXIST, ONLY_BACKUP_EXIST, ONLY_LEGACY_BACKUP_EXIST])
def test_force_delete_profile_deletes_backup_files(profile_name: str) -> None:
    # ARRANGE
    copy_blank_profile_files(safe_settings.data_path)

    # ACT
    PersistentStorageService.delete_profile(profile_name, force=True)

    # ASSERT
    actual_profiles = PersistentStorageService.list_stored_profile_names()
    assert profile_name not in actual_profiles, f"Profile `{profile_name}` deletion should be successful"

    assert not backup_files_exists(profile_name), f"Backup files for profile `{profile_name}` should be also deleted"
