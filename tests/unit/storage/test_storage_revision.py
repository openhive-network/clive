from __future__ import annotations

from typing import Final

import pytest
import test_tools as tt
from beekeepy import AsyncBeekeeper

from clive.__private.core.commands.create_profile_wallets import CreateProfileWallets
from clive.__private.core.commands.save_profile import SaveProfile
from clive.__private.core.profile import Profile
from clive.__private.settings import safe_settings
from clive.__private.storage import ProfileStorageModel
from clive.__private.storage.service import PersistentStorageService
from clive.__private.storage.storage_history import StorageHistory

REVISIONS: Final[list[str]] = ["ffc97b51", "a721f943", "9c46df0c"]
LATEST_REVISION: Final[str] = REVISIONS[-1]

FIRST_PROFILE_NAME: Final[str] = "first"


async def create_and_save_profile(profile_name: str) -> None:
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


def test_storage_revision_doesnt_changed_for_latest_version() -> None:
    # ACT
    actual_revision = ProfileStorageModel.get_this_revision()

    # ASSERT
    message = (
        "Storage model revision has changed. If you are sure that it is expected, please update the expected revision."
    )
    assert actual_revision == LATEST_REVISION, message


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


async def test_storage_revision_doesnt_changed_in_known_versions() -> None:
    # ARRANGE
    info_message = (
        "Revision hash in older storage versions shouldn't change, it means older storage"
        " versions may not be loaded properly, if you are sure this is expected check tests with"
        " loading of first profile revision including profile with transaction or alarms"
    )

    assert StorageHistory.get_revisions() == REVISIONS, info_message


@pytest.mark.parametrize("file_name", ["vv1.profile", "v1.backup", "v2.2profile", "v2.2.profile"])
async def test_profile_name_invalid(file_name: str) -> None:
    # ARRANGE
    storage_data_dir = tt.context.get_current_directory() / "clive/data"
    profile_path = storage_data_dir / "alice" / file_name

    # ACT & ASSERT
    with pytest.raises(AssertionError, match=f"Looks like {profile_path} is not a profile file."):
        PersistentStorageService._model_cls_from_path(profile_path)
