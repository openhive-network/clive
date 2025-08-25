from __future__ import annotations

import pytest

from clive.__private.settings import safe_settings
from clive.__private.storage.service.service import PersistentStorageService
from clive_local_tools.storage_migration import BLANK_PROFILES, copy_blank_profile_files


@pytest.fixture(autouse=True)
def prepared_storage() -> None:
    copy_blank_profile_files(safe_settings.data_path)


@pytest.mark.parametrize("profile_name", BLANK_PROFILES)
def test_profile_exists(profile_name: str) -> None:
    # ARRANGE
    copy_blank_profile_files(safe_settings.data_path)

    # ACT
    is_stored = PersistentStorageService.is_profile_stored(profile_name)

    # ASSERT
    assert is_stored, f"Profile `{profile_name}` is not visible in storage"
