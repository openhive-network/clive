from __future__ import annotations

import pytest

from clive.__private.core.profile_data import ProfileCouldNotBeLoadedError
from clive.__private.core.world import TyperWorld, World


def test_if_profile_is_loaded(world: World, wallet_name: str) -> None:
    # ARRANGE, ACT & ASSERT
    assert world.profile_data.name == wallet_name


def test_if_lastly_used_profile_is_loaded() -> None:
    # ARRANGE
    expected_profile_name = "first"
    world = World(expected_profile_name)
    world.profile_data.save()  # this one should be lastly used
    world.close()  # close world so beekeeper can be closed

    # ACT
    world = World()

    # ASSERT
    assert world.profile_data.list_profiles() == [expected_profile_name]


def test_if_correct_profile_is_loaded_when_something_is_stored() -> None:
    # ARRANGE
    expected_profile_name = "first"
    additional_profile_name = "second"
    world = World(additional_profile_name)
    world.profile_data.save()  # lastly used is other than we're loading
    world.close()  # close world so beekeeper can be closed

    # ACT
    world = World(expected_profile_name)

    # ASSERT
    assert world.profile_data.name == expected_profile_name


@pytest.mark.parametrize("world_cls", [World, TyperWorld])
def test_loading_profile_without_given_name_when_no_lastly_used(world_cls: type[World]) -> None:
    # ACT & ASSERT
    with pytest.raises(ProfileCouldNotBeLoadedError) as error:
        world_cls()
    assert "No lastly used profile to load." in str(error.value)


def test_loading_non_existing_profile_with_auto_create_disabled() -> None:
    # ARRANGE
    profile_name = "non_existing_profile"
    exception_message = f"Profile `{profile_name}` does not exist."

    # ACT & ASSERT
    with pytest.raises(ProfileCouldNotBeLoadedError) as error:
        TyperWorld(profile_name)
    assert exception_message in str(error.value)


def test_loading_existing_profile_with_auto_create_disabled() -> None:
    # ARRANGE
    profile_name = "existing_profile"
    world = World(profile_name)
    world.profile_data.save()
    world.close()

    # ACT & ASSERT
    world = TyperWorld(profile_name)
    assert world.profile_data.name == profile_name
