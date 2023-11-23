from __future__ import annotations

import pytest

from clive.__private.core.profile_data import NoDefaultProfileToLoadError, ProfileData, ProfileDoesNotExistsError
from clive.__private.core.world import TyperWorld, World


def test_if_profile_is_loaded(world: World, wallet_name: str) -> None:
    # ARRANGE, ACT & ASSERT
    assert world.profile_data.name == wallet_name


async def test_if_first_profile_is_saved_as_a_default_one() -> None:
    # ARRANGE
    expected_profile_name = "first"

    # This profile should be saved as a default one
    async with World(expected_profile_name, use_beekeeper=False):
        pass  # save should be called on exit

    # ACT
    # Creating world without given profile name should load the default one
    async with World(use_beekeeper=False) as world:
        loaded_profile_name = world.profile_data.name

    # ASSERT
    assert loaded_profile_name == expected_profile_name
    assert ProfileData.get_default_profile_name() == expected_profile_name
    assert ProfileData.list_profiles() == [expected_profile_name]


async def test_if_correct_profile_is_loaded_when_default_is_stored() -> None:
    # ARRANGE
    default_profile_name = "first"
    additional_profile_name = "second"

    # This profile should be saved as a default one
    async with World(additional_profile_name, use_beekeeper=False):
        pass  # save should be called on exit

    # ACT
    # Explicitly loading the expected profile, even when there is a default one
    async with World(default_profile_name, use_beekeeper=False) as world:
        loaded_profile_name = world.profile_data.name

    # ASSERT
    assert loaded_profile_name == default_profile_name
    assert ProfileData.get_default_profile_name() == additional_profile_name
    assert ProfileData.list_profiles() == [default_profile_name, additional_profile_name]


async def test_if_default_profile_is_loaded_other_was_saved() -> None:
    # ARRANGE
    default_profile_name = "first"
    additional_profile_name = "second"

    # This profile should be saved as a default one
    async with World(default_profile_name, use_beekeeper=False):
        pass  # save should be called on exit

    # ACT
    # Explicitly loading the other profile should not change the default one
    async with World(additional_profile_name, use_beekeeper=False) as world:
        explicitly_loaded_profile_name = world.profile_data.name

    # Check if the default profile is loaded
    async with World(use_beekeeper=False) as world:
        default_loaded_profile_name = world.profile_data.name

    # ASSERT
    assert explicitly_loaded_profile_name == additional_profile_name
    assert default_loaded_profile_name == default_profile_name
    assert ProfileData.get_default_profile_name() == default_profile_name
    assert ProfileData.list_profiles() == [default_profile_name, additional_profile_name]


@pytest.mark.parametrize("world_cls", [World, TyperWorld])
def test_loading_profile_without_given_name_when_no_default_set(world_cls: type[World]) -> None:
    # ACT & ASSERT
    with pytest.raises(NoDefaultProfileToLoadError):
        world_cls()


def test_loading_non_existing_profile_with_auto_create_disabled() -> None:
    # ARRANGE
    profile_name = "non_existing_profile"
    exception_message = f"Profile `{profile_name}` does not exist."

    # ACT & ASSERT
    with pytest.raises(ProfileDoesNotExistsError) as error:
        # TyperWorld should have auto_create disabled by default
        TyperWorld(profile_name)
    assert exception_message in str(error.value)


async def test_loading_existing_profile_with_auto_create_disabled() -> None:
    # ARRANGE
    profile_name = "existing_profile"

    # This profile should be saved as a default one
    async with World(profile_name, use_beekeeper=False):
        pass  # save should be called on exit

    # ACT
    async with World(profile_name, use_beekeeper=False) as world:
        loaded_profile_name = world.profile_data.name

    # ASSERT
    assert loaded_profile_name == profile_name
    assert ProfileData.get_default_profile_name() == profile_name
    assert ProfileData.list_profiles() == [profile_name]
