from __future__ import annotations

from typing import Final

import pytest
import test_tools as tt
from beekeepy import AsyncBeekeeper

from clive.__private.core.commands.create_profile_wallets import CreateProfileWallets
from clive.__private.core.commands.save_profile import SaveProfile
from clive.__private.core.profile import Profile
from clive.__private.settings import safe_settings
from clive.__private.storage.model import ProfileStorageModel
from clive.__private.storage.service import ModelDoesNotExistsError, PersistentStorageService

PROFILE_FILE_LIST: Final[tuple[str, ...]] = ("v0.profile", "v1.profile", "v2.profile")
EXPECTED_REVISION_LIST: Final[tuple[str, ...]] = ("70b94758", "00ad2058", "76cd0378")
EXPECTED_REVISION: Final[str] = EXPECTED_REVISION_LIST[-1]
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


def test_storage_revision_doesnt_changed() -> None:
    # ACT
    actual_revision = ProfileStorageModel.calculate_storage_model_revision()

    # ASSERT
    message = (
        "Storage model revision has changed. If you are sure that it is expected, please update the expected revision."
    )
    assert actual_revision == EXPECTED_REVISION, message


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


@pytest.mark.parametrize(("file_name", "expected_hash"), zip(PROFILE_FILE_LIST, EXPECTED_REVISION_LIST, strict=True))
async def test_storage_revision_hash_in_older_versions(file_name: str, expected_hash: str) -> None:
    # ARRANGE
    info_message = (
        "Revision hash in older storage versions shouldn't change, it means older storage"
        " versions may not be loaded properly, if you are sure this is expected check tests with"
        " loading of first profile revision including profile with transaction or alarms"
    )
    storage_data_dir = tt.context.get_current_directory() / "clive/data"
    profile_path = storage_data_dir / file_name

    # ACT & ASSERT
    model_cls = PersistentStorageService._model_cls_from_path(profile_path)
    actual_hash = model_cls.calculate_storage_model_revision()
    assert actual_hash == expected_hash, f"{actual_hash=} {expected_hash=}\n{info_message}"


@pytest.mark.parametrize("file_name", ["vv1.profile", "v1.backup", "v2.2profile", "v2.2.profile"])
async def test_profile_name_invalid(file_name: str) -> None:
    # ARRANGE
    storage_data_dir = tt.context.get_current_directory() / "clive/data"
    profile_path = storage_data_dir / file_name

    # ACT & ASSERT
    with pytest.raises(ModelDoesNotExistsError, match="Model not found"):
        PersistentStorageService._model_cls_from_path(profile_path)
