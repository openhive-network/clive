from __future__ import annotations

from typing import Final

from beekeepy import AsyncBeekeeper

from clive.__private.core.commands.create_profile_wallets import CreateProfileWallets
from clive.__private.core.commands.save_profile import SaveProfile
from clive.__private.core.profile import Profile
from clive.__private.settings import safe_settings
from clive.__private.storage import ProfileStorageModel
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


async def test_storage_revision_doesnt_changed_in_known_versions() -> None:
    # ARRANGE
    info_message = (
        "Revision hash in older storage versions shouldn't change, it means older storage"
        " versions may not be loaded properly, if you are sure this is expected check tests with"
        " loading of first profile revision including profile with transaction or alarms"
    )

    # ACT
    assert StorageHistory.get_revisions() == REVISIONS, info_message
