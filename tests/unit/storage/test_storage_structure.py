from __future__ import annotations

import pytest

from clive.__private.storage.service import ModelDoesNotExistsError, PersistentStorageService
from tests.unit.storage.test_storage_revision import FIRST_PROFILE_NAME, create_and_save_profile


async def test_storage_dir_contains_expected_files() -> None:
    # ARRANGE
    storage_data_dir = PersistentStorageService._get_storage_directory()
    profile_dir = PersistentStorageService.get_profile_directory(FIRST_PROFILE_NAME)
    profile_file_path = profile_dir / PersistentStorageService.get_current_version_profile_filename()

    # ACT
    # saving a profile will cause persisting storage data to be saved
    await create_and_save_profile(FIRST_PROFILE_NAME)

    # ASSERT
    assert storage_data_dir.is_dir(), "Storage data path is not a directory or is missing."
    assert profile_dir.is_dir(), f"Expected profile directory {profile_dir} is not a directory or is missing."
    assert profile_file_path.is_file(), "Profile file is not a file or is missing."
    assert profile_file_path.read_text(), "Profile file is empty."


@pytest.mark.parametrize(
    "file_name",
    [
        "vv1.profile",
        "v1.backup",
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
    profile_dir = PersistentStorageService.get_profile_directory("invalid_profile_file_name_test")
    profile_dir.mkdir(parents=True, exist_ok=True)
    profile_file_path = profile_dir / file_name
    profile_file_path.touch()

    # ACT & ASSERT
    with pytest.raises(ModelDoesNotExistsError, match=f"Model not found for profile stored at `{file_name}`."):
        PersistentStorageService._model_cls_from_path(profile_file_path)
