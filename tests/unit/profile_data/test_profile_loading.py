from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

import clive

if TYPE_CHECKING:
    from clive.__private.core.world import World


def test_if_profile_is_loaded(world: World, wallet_name: str) -> None:
    # ARRANGE, ACT & ASSERT
    assert world.profile_data.name == wallet_name


@pytest.mark.skip(reason="no idea how to recreate")
def test_if_lastly_used_profile_is_loaded() -> None:
    # ARRANGE
    expected_profile_name = "first"
    world = clive.World(expected_profile_name)
    world.profile_data.save()  # this one should be lastly used

    # ACT
    world = clive.World()

    # ASSERT
    assert world.profile_data.list_profiles() == [expected_profile_name]


@pytest.mark.skip(reason="no idea how to recreate")
def test_if_correct_profile_is_loaded_when_something_is_stored() -> None:
    # ARRANGE
    expected_profile_name = "first"
    additional_profile_name = "second"
    world = clive.World(additional_profile_name)
    world.profile_data.save()  # lastly used is other than we're loading

    # ACT
    world = clive.World(expected_profile_name)

    # ASSERT
    assert world.profile_data.name == expected_profile_name


@pytest.mark.skip(reason="no idea how to recreate")
def test_loading_profile_without_given_name_when_no_lastly_used() -> None:
    # ACT
    world = clive.World()

    # ASSERT
    assert world.profile_data.name == ""  # noqa PLC1901 TODO: Should we allow for empty profile name? Probably not
