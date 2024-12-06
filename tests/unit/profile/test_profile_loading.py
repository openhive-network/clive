from __future__ import annotations

import pytest

from clive.__private.core.beekeeper.handle import Beekeeper
from clive.__private.core.commands.create_wallet import CreateWallet
from clive.__private.core.commands.exceptions import NoProfileUnlockedError
from clive.__private.core.profile import Profile
from clive.__private.core.world import CLIWorld, World
from clive.__private.storage.service import ProfileDoesNotExistsError
from clive_local_tools.data.generates import generate_wallet_password


@pytest.fixture
def beekeeper_for_remote_use() -> Beekeeper:
    return Beekeeper()


async def create_unlocked_wallet(beekeeper: Beekeeper, wallet_name: str) -> None:
    await CreateWallet(beekeeper=beekeeper, wallet=wallet_name, password=generate_wallet_password()).execute()


def test_if_profile_is_loaded(world: World, wallet_name: str) -> None:
    # ARRANGE, ACT & ASSERT
    assert world.profile.name == wallet_name


async def test_if_unlocked_profile_is_loaded_other_was_saved(beekeeper_for_remote_use: Beekeeper) -> None:
    # ARRANGE
    additional_profile_name = "first"
    unlocked_profile_name = "second"
    additional_profile_name2 = "third"
    profile_names = sorted([additional_profile_name, unlocked_profile_name, additional_profile_name2])
    for profile_name in profile_names:
        Profile.create(profile_name).save()

    # This profile should be unlocked
    await create_unlocked_wallet(beekeeper_for_remote_use, unlocked_profile_name)

    # ACT
    # Check if the unlocked profile is loaded
    async with World(beekeeper_remote_endpoint=beekeeper_for_remote_use.http_endpoint) as world_cm:
        loaded_profile_name = world_cm.profile.name

    # ASSERT
    assert loaded_profile_name == unlocked_profile_name
    assert Profile.get_default_profile_name() == unlocked_profile_name
    assert Profile.list_profiles() == profile_names


@pytest.mark.parametrize("world_cls", [World, CLIWorld])
def test_loading_profile_without_beekeeper_session(world_cls: type[World]) -> None:
    # ACT & ASSERT
    with pytest.raises(NoProfileUnlockedError):
        world_cls()


async def test_loading_non_existing_profile_with_auto_create_disabled(beekeeper_for_remote_use: Beekeeper) -> None:
    # ARRANGE
    profile_name = "non_existing_profile"
    exception_message = f"Profile `{profile_name}` does not exist."

    await create_unlocked_wallet(beekeeper_for_remote_use, profile_name)

    # ACT & ASSERT
    with pytest.raises(ProfileDoesNotExistsError) as error:
        # CLIWorld should have auto_create disabled by default
        await CLIWorld(beekeeper_remote_endpoint=beekeeper_for_remote_use.http_endpoint).setup()
    assert exception_message in str(error.value)


async def test_loading_existing_profile_with_auto_create_disabled(beekeeper_for_remote_use: Beekeeper) -> None:
    # ARRANGE
    profile_name = "existing_profile"

    Profile.create(profile_name).save()
    await create_unlocked_wallet(beekeeper_for_remote_use, profile_name)

    # ACT
    async with World(beekeeper_remote_endpoint=beekeeper_for_remote_use.http_endpoint) as world:
        loaded_profile_name = world.profile.name

    # ASSERT
    assert loaded_profile_name == profile_name
    assert Profile.get_default_profile_name() == profile_name
    assert Profile.list_profiles() == [profile_name]
