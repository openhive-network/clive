from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt
from beekeepy import AsyncBeekeeper

from clive.__private.core.commands.create_profile_wallets import CreateProfileWallets
from clive.__private.core.commands.save_profile import SaveProfile
from clive.__private.core.profile import Profile
from clive.__private.settings import safe_settings
from clive.__private.storage import migrations
from clive.__private.storage.model import calculate_storage_model_revision, get_storage_version
from clive.__private.storage.service import PersistentStorageService

if TYPE_CHECKING:
    from typing import Callable

EXPECTED_REVISION_HASH: Final[str] = "ec33120b"
EXPECTED_VERSION: Final[str] = "v2"
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
    actual_revision_hash = calculate_storage_model_revision()
    actual_version = get_storage_version()

    # ASSERT
    message = (
        "Storage model revision has changed. If you are sure that it is expected,"
        " please update the expected revision."
    )
    assert actual_revision_hash == EXPECTED_REVISION_HASH, message
    assert actual_version == EXPECTED_VERSION, "Storage model version has changed."


async def test_storage_dir_contains_expected_files() -> None:
    # ARRANGE
    storage_data_dir = tt.context.get_current_directory() / "clive/data"
    version_dir = storage_data_dir / EXPECTED_VERSION
    filename = PersistentStorageService.get_profile_filename(FIRST_PROFILE_NAME)
    profile_file = storage_data_dir / version_dir / filename

    # ACT
    # saving a profile will cause persisting storage data to be saved
    await create_and_save_profile(FIRST_PROFILE_NAME)

    # ASSERT
    assert storage_data_dir.is_dir(), "Storage data path is not a directory or is missing."
    assert version_dir.is_dir(), f"Expected revision directory {version_dir} is not a directory or is missing."
    assert profile_file.is_file(), "Profile file is not a file or is missing."
    assert profile_file.read_text(), "Profile file is empty."


@pytest.mark.parametrize(
    ("func", "expected_hash"),
    [
        (migrations.v1.calculate_storage_model_revision, "b17e241d"),
        (migrations.v2.calculate_storage_model_revision, "ec33120b"),
    ],
    ids=["version_1", "version_2"],
)
async def test_storage_revision_hash_in_older_versions(func: Callable[[], str], expected_hash: str) -> None:
    message = (
        "Revision hash in older storage versions shouldn't change,"
        " it means older storage versions may not be loaded properly and migration"
        " of storage might not work properly, check cli tests for performing storage migration"
    )
    assert func() == expected_hash, message
