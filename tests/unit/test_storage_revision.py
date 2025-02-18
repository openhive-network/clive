from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final

import test_tools as tt
from beekeepy import AsyncBeekeeper

from clive.__private.core.commands.create_wallet import CreateWallet
from clive.__private.core.encryption import EncryptionService
from clive.__private.core.profile import Profile
from clive.__private.core.wallet_container import WalletContainer
from clive.__private.settings import safe_settings
from clive.__private.storage.model import ProfileStorageModelSchema, calculate_storage_model_revision
from clive.__private.storage.service import PersistentStorageService

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch

EXPECTED_REVISION: Final[str] = "c600278a"
FIRST_PROFILE_NAME: Final[str] = "first"


async def create_and_save_profile(profile_name: str) -> None:
    async with await AsyncBeekeeper.factory(settings=safe_settings.beekeeper.settings_local_factory()) as beekeeper:
        result = await CreateWallet(
            session=await beekeeper.session, wallet_name=profile_name, password=profile_name
        ).execute_with_result()
        encryption_service = EncryptionService(
            WalletContainer(result.unlocked_user_wallet, result.unlocked_encryption_wallet)
        )
        await Profile.create(profile_name).save(encryption_service)


def test_storage_revision_doesnt_changed() -> None:
    # ACT
    actual_revision = calculate_storage_model_revision()

    # ASSERT
    message = (
        "Storage model revision has changed. If you are sure that it is expected,"
        " please update the expected revision."
    )
    assert actual_revision == EXPECTED_REVISION, message


async def test_storage_dir_contains_expected_files() -> None:
    # ARRANGE
    storage_data_dir = tt.context.get_current_directory() / "clive/data"
    current_revision_symlink = storage_data_dir / "current"
    revision_dir = storage_data_dir / EXPECTED_REVISION
    filename = PersistentStorageService.get_profile_filename(FIRST_PROFILE_NAME)
    profile_json_file = storage_data_dir / revision_dir / filename

    # ACT
    # saving a profile will cause persisting storage data to be saved
    await create_and_save_profile(FIRST_PROFILE_NAME)

    # ASSERT
    assert storage_data_dir.is_dir(), "Storage data path is not a directory or is missing."
    assert current_revision_symlink.is_symlink(), "Current revision path is not a symlink or is missing."
    assert revision_dir.is_dir(), "Revision dir is not a directory or is missing."
    assert (
        current_revision_symlink.resolve() == revision_dir
    ), "Current revision symlink does not point to the expected revision dir."
    assert profile_json_file.is_file(), "Profile JSON file is not a file or is missing."
    assert profile_json_file.read_text(), "Profile JSON file is empty."


async def test_correct_revision_is_loaded_when_multiple_ones_exist(monkeypatch: MonkeyPatch) -> None:
    # ARRANGE
    storage_data_dir = tt.context.get_current_directory() / "clive/data"
    current_revision_symlink = storage_data_dir / "current"
    new_revision_dir = storage_data_dir / "ee087417"
    profile_name_in_new_revision = "second"

    def mock_schema_json(*, by_alias: bool = False, ref_template: str = "", **dumps_kwargs: Any) -> str:  # noqa: ARG001
        """Mock used for simulating the situation when the schema has changed."""
        return "anything"

    # ACT & ASSERT
    # we need to have more than one revision of profile data for this test
    await create_and_save_profile(FIRST_PROFILE_NAME)

    # stimulate the situation when the schema has changed, causing different revision
    monkeypatch.setattr(ProfileStorageModelSchema, "schema_json", mock_schema_json)

    assert not new_revision_dir.is_dir(), "New revision dir should not yet exist."
    assert Profile.list_profiles() == [], "There should be no profiles yet in new revision."

    await create_and_save_profile(profile_name_in_new_revision)

    assert new_revision_dir.is_dir(), "New revision dir should exist."

    message = "Current revision symlink should point to new revision."
    assert current_revision_symlink.resolve() == new_revision_dir, message

    message = "There should be only one profile saved in new revision."
    assert Profile.list_profiles() == [profile_name_in_new_revision], message
