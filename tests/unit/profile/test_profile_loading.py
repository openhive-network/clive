from __future__ import annotations

import pytest
from test_tools.__private.exceptions import CommunicationError

from clive.__private.core.beekeeper import Beekeeper
from clive.__private.core.commands.create_profile_encryption_wallet import CreateProfileEncryptionWallet
from clive.__private.core.profile import Profile
from clive.__private.core.world import CLIWorld, World
from clive.__private.storage.service import (
    NoDefaultProfileToLoadError,
    PersistentStorageService,
)


async def save_new_profile(beekeeper: Beekeeper, profile: Profile) -> None:
    await CreateProfileEncryptionWallet(beekeeper=beekeeper, profile_name=profile.name, password=None).execute()
    await PersistentStorageService(beekeeper).save_profile(profile)


def test_if_profile_is_loaded(world: World, wallet_name: str) -> None:
    # ARRANGE, ACT & ASSERT
    assert world.profile.name == wallet_name


async def test_if_first_profile_is_saved_as_a_default_one() -> None:
    # ARRANGE
    expected_profile_name = "first"

    # This profile should be saved as a only one which makes this profile default
    profile = Profile(expected_profile_name)
    async with Beekeeper() as beekeeper_cm:
        await save_new_profile(beekeeper_cm, profile)

        # ACT
        # Creating world without given profile name should load the default one
        async with World() as world:
            loaded_profile_name = world.profile.name

        # ASSERT
        assert loaded_profile_name == expected_profile_name
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
        async with World() as world:
            loaded_profile_name = world.profile.name

        # ASSERT
        assert loaded_profile_name == profile.name
        with pytest.raises(NoDefaultProfileToLoadError):
            PersistentStorageService.get_default_profile_name()
        assert PersistentStorageService.list_stored_profile_names() == [profile.name, additional_profile.name]


@pytest.mark.parametrize("world_cls", [World, CLIWorld])
async def test_loading_profile_beekeeper_not_unlocked(world_cls: type[World]) -> None:
    # ARRANGE
    profile = Profile("first")

    async with Beekeeper() as beekeeper_cm:
        await save_new_profile(beekeeper_cm, profile)
        await beekeeper_cm.api.lock_all()

        # ACT & ASSERT
        with pytest.raises(CommunicationError):
            async with world_cls():
                ...
