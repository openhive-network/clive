from __future__ import annotations

import pytest

from clive.__private.settings import safe_settings
from clive.__private.storage.service import MultipleProfileVersionsError, PersistentStorageService
from clive_local_tools.storage_migration.helpers import ALL_PROFILES, copy_prepared_profiles_data


@pytest.fixture(autouse=True)
def _prepare_profiles_in_old_version() -> None:
    copy_prepared_profiles_data(safe_settings.data_path)


def test_list_profiles() -> None:
    # ACT
    profiles = PersistentStorageService.list_stored_profile_names()

    # ASSERT
    assert tuple(profiles) == ALL_PROFILES, f"Actual profiles are `{profiles}`, expected are `{ALL_PROFILES}`"


@pytest.mark.parametrize("profile_name", ["two", "three", "mary"])
def test_delete_profile_force_not_required(profile_name: str) -> None:
    # ACT
    PersistentStorageService.delete_profile(profile_name)

    # ASSERT
    actual_profiles = PersistentStorageService.list_stored_profile_names()
    assert profile_name not in actual_profiles, f"Profile `{profile_name}` was not deleted"


@pytest.mark.parametrize("profile_name", ["one"])
def test_delete_profile_with_force(profile_name: str) -> None:
    # ACT
    PersistentStorageService.delete_profile(profile_name, force=True)

    # ASSERT
    actual_profiles = PersistentStorageService.list_stored_profile_names()
    assert profile_name not in actual_profiles, f"Profile `{profile_name}` was not deleted"


@pytest.mark.parametrize("profile_name", ["one"])
def test_try_delete_profile_without_force(profile_name: str) -> None:
    # ARRANGE
    message = f"Multiple versions or backups of profile `{profile_name}` exist."

    # ACT & ASSERT
    with pytest.raises(MultipleProfileVersionsError, match=message):
        PersistentStorageService.delete_profile(profile_name)


@pytest.mark.parametrize("profile_name", ALL_PROFILES)
def test_profile_exists(profile_name: str) -> None:
    # ACT
    is_stored = PersistentStorageService.is_profile_stored(profile_name)

    # ASSERT
    assert is_stored, f"Profile `{profile_name}` is not visible in storage"
