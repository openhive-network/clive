from __future__ import annotations

import pytest
import test_tools as tt

from clive.__private.storage.service import PersistentStorageService
from tests.unit.storage.test_storage_revision import FIRST_PROFILE_NAME, create_and_save_profile


async def test_storage_dir_contains_expected_files() -> None:
    # ARRANGE
    storage_data_dir = tt.context.get_current_directory() / "clive/data"
    profile_dir = storage_data_dir / FIRST_PROFILE_NAME
    profile_file_path = profile_dir / PersistentStorageService.get_current_version_profile_filename()

    # ACT
    # saving a profile will cause persisting storage data to be saved
    await create_and_save_profile(FIRST_PROFILE_NAME)

    # ASSERT
    assert storage_data_dir.is_dir(), "Storage data path is not a directory or is missing."
    assert profile_dir.is_dir(), f"Expected profile directory {profile_dir} is not a directory or is missing."
    assert profile_file_path.is_file(), "Profile file is not a file or is missing."
    assert profile_file_path.read_text(), "Profile file is empty."


@pytest.mark.parametrize("file_name", ["vv1.profile", "v1.backup", "v2.2profile", "v2.2.profile"])
async def test_profile_name_invalid(file_name: str) -> None:
    # ARRANGE
    storage_data_dir = tt.context.get_current_directory() / "clive/data"
    profile_path = storage_data_dir / "alice" / file_name
    # ACT & ASSERT
    with pytest.raises(AssertionError, match=f"Looks like {profile_path} is not a profile file."):
        PersistentStorageService._model_cls_from_path(profile_path)
