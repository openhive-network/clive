from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
from beekeepy import AsyncBeekeeper

from clive.__private.core.commands.create_profile_wallets import CreateProfileWallets
from clive.__private.core.commands.save_profile import SaveProfile
from clive.__private.core.profile import Profile
from clive.__private.settings import safe_settings
from clive.__private.storage.service.service import PersistentStorageService

if TYPE_CHECKING:
    from pathlib import Path

FIRST_PROFILE_NAME: Final[str] = "first"


async def _create_and_save_profile(profile_name: str) -> None:
    async with await AsyncBeekeeper.factory(settings=safe_settings.beekeeper.settings_local_factory()) as beekeeper:
        result = await CreateProfileWallets(
            session=await beekeeper.session, profile_name=profile_name, password=profile_name
        ).execute_with_result()
        profile = Profile.create(profile_name)
        await SaveProfile(
            profile=profile,
            unlocked_wallet=result.unlocked_user_wallet,
            unlocked_encryption_wallet=result.unlocked_encryption_wallet,
        ).execute()


def _create_stub_profile_file(file_name: str) -> Path:
    profile_dir = PersistentStorageService.get_profile_directory("stub_profile")
    profile_dir.mkdir(parents=True, exist_ok=True)
    profile_file_path = profile_dir / file_name
    profile_file_path.touch()
    return profile_file_path


async def test_storage_dir_contains_expected_files() -> None:
    # ARRANGE
    storage_data_dir = PersistentStorageService._get_storage_directory()
    profile_dir = PersistentStorageService.get_profile_directory(FIRST_PROFILE_NAME)
    profile_file_path = profile_dir / PersistentStorageService.get_current_version_profile_filename()

    # ACT
    # saving a profile will cause persisting storage data to be saved
    await _create_and_save_profile(FIRST_PROFILE_NAME)

    # ASSERT
    assert storage_data_dir.is_dir(), "Storage data path is not a directory or is missing."
    assert profile_dir.is_dir(), f"Expected profile directory {profile_dir} is not a directory or is missing."
    assert profile_file_path.is_file(), "Profile file is not a file or is missing."
    assert profile_file_path.read_text(), "Profile file is empty."


@pytest.mark.parametrize("file_name", ["v1.profile", "v2.profile", "v2.backup"])
async def test_valid_profile_file_name(file_name: str) -> None:
    # ARRANGE
    profile_file_path = _create_stub_profile_file(file_name)

    # ACT
    version = PersistentStorageService.get_version_from_profile_file(profile_file_path)

    # ASSERT
    assert version, "If the file name is valid, the version should be extracted from it."


@pytest.mark.parametrize(
    "file_name",
    [
        "vv1.profile",
        "v2.2profile",
        "v2.2.profile",
        "2.profile",
        "2.2.profile",
        ".profile",
        "v2.backup.profile",
    ],
)
async def test_invalid_profile_file_name(file_name: str) -> None:
    # ARRANGE
    profile_file_path = _create_stub_profile_file(file_name)

    # ACT
    version = PersistentStorageService.get_version_from_profile_file(profile_file_path)

    # ASSERT
    assert version is None, "If the file name is invalid, we should get None"
