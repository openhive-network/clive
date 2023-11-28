from __future__ import annotations

import pytest

from clive.__private.core.profile_data import NoLastlyUsedProfileError, ProfileData, ProfileDoesNotExistsError
from clive.__private.core.world import TyperWorld, World


def test_if_profile_is_loaded(world: World, wallet_name: str) -> None:
    # ARRANGE, ACT & ASSERT
    assert world.profile_data.name == wallet_name


async def test_if_lastly_used_profile_is_loaded() -> None:
    # ARRANGE
    expected_profile_name = "first"

    async with World(expected_profile_name, use_beekeeper=False):
        pass  # save should be called on exit

    # ACT
    async with World(use_beekeeper=False) as world:
        loaded_profile_name = world.profile_data.name

    # ASSERT
    assert loaded_profile_name == expected_profile_name
    assert ProfileData.list_profiles() == [expected_profile_name]


async def test_if_correct_profile_is_loaded_when_something_is_stored() -> None:
    # ARRANGE
    expected_profile_name = "first"
    additional_profile_name = "second"

    async with World(additional_profile_name, use_beekeeper=False):
        pass  # save should be called on exit

    # ACT
    async with World(expected_profile_name, use_beekeeper=False) as world:
        loaded_profile_name = world.profile_data.name

    # ASSERT
    assert loaded_profile_name == expected_profile_name
    assert ProfileData.list_profiles() == [expected_profile_name, additional_profile_name]


@pytest.mark.parametrize("world_cls", [World, TyperWorld])
def test_loading_profile_without_given_name_when_no_lastly_used(world_cls: type[World]) -> None:
    # ACT & ASSERT
    with pytest.raises(NoLastlyUsedProfileError):
        world_cls()


def test_loading_non_existing_profile_with_auto_create_disabled() -> None:
    # ARRANGE
    profile_name = "non_existing_profile"
    exception_message = f"Profile `{profile_name}` does not exist."

    # ACT & ASSERT
    with pytest.raises(ProfileDoesNotExistsError) as error:
        TyperWorld(profile_name)
    assert exception_message in str(error.value)


async def test_loading_existing_profile_with_auto_create_disabled() -> None:
    # ARRANGE
    profile_name = "existing_profile"

    async with World(profile_name, use_beekeeper=False):
        pass  # save should be called on exit

    # ACT
    async with World(profile_name, use_beekeeper=False) as world:
        loaded_profile_name = world.profile_data.name

    # ASSERT
    assert loaded_profile_name == profile_name
    assert ProfileData.list_profiles() == [profile_name]
