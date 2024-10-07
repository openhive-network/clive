from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive.__private.core.beekeeper import Beekeeper
from clive.__private.core.commands.create_profile_encryption_wallet import CreateProfileEncryptionWallet
from clive.__private.core.commands.create_wallet import CreateWallet
from clive.__private.core.commands.exceptions import ProfileNotUnlockedError
from clive.__private.core.encryption import EncryptionService
from clive.__private.core.profile import Profile
from clive.__private.storage.service import (
    NoDefaultProfileToLoadError,
    PersistentStorageService,
)

if TYPE_CHECKING:
    from clive.__private.core.world import World


async def save_new_profile(beekeeper: Beekeeper, profile: Profile) -> None:
    await CreateProfileEncryptionWallet(beekeeper=beekeeper, profile_name=profile.name, password=None).execute()
    await CreateWallet(beekeeper=beekeeper, wallet=profile.name, password=None).execute()
    encryption_service = await EncryptionService.from_beekeeper(beekeeper)
    await profile.save(encryption_service)


def test_if_profile_is_loaded(world: World, prepare_profile_with_session: Profile) -> None:
    # ARRANGE, ACT & ASSERT
    assert world.profile.name == prepare_profile_with_session.name


async def test_if_first_profile_is_saved_as_a_default_one() -> None:
    # ARRANGE
    expected_profile_name = "first"

    # This profile should be saved as a only one which makes this profile default
    profile = Profile(expected_profile_name)
    async with Beekeeper() as beekeeper_cm:
        await save_new_profile(beekeeper_cm, profile)

        # ACT
        # ASSERT
        assert PersistentStorageService.get_default_profile_name() == expected_profile_name
        assert PersistentStorageService.list_stored_profile_names() == [expected_profile_name]


async def test_if_profile_is_loaded_when_other_was_saved() -> None:
    # ARRANGE
    profile = Profile("first")
    additional_profile = Profile("second")

    async with Beekeeper() as beekeeper_cm:
        await save_new_profile(beekeeper_cm, additional_profile)
        await beekeeper_cm.api.lock_all()

        # Both profiles should be saved and beekeeper should have unlocked first profile encryption wallet
        await save_new_profile(beekeeper_cm, profile)

        # ACT
        # Check if the first profile is loaded
        encryption_service = await EncryptionService.from_beekeeper(beekeeper_cm)
        loaded_profile = await PersistentStorageService(encryption_service).load_profile()

        # ASSERT
        assert loaded_profile.name == profile.name
        with pytest.raises(NoDefaultProfileToLoadError):
            PersistentStorageService.get_default_profile_name()
        assert PersistentStorageService.list_stored_profile_names() == [profile.name, additional_profile.name]


async def test_loading_profile_beekeeper_not_unlocked() -> None:
    # ARRANGE
    profile = Profile("first")

    async with Beekeeper() as beekeeper_cm:
        await save_new_profile(beekeeper_cm, profile)
        await beekeeper_cm.api.lock_all()

        # ACT
        # ASSERT
        with pytest.raises(ProfileNotUnlockedError):
            await EncryptionService.from_beekeeper(beekeeper_cm)
