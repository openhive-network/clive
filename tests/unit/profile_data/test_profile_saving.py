from __future__ import annotations

import clive


def test_if_profile_is_saved() -> None:
    # ARRANGE
    expected_profile_name = "first"

    # ACT
    world = clive.World(expected_profile_name)
    world.profile_data.save()

    # ASSERT
    assert world.profile_data.list_profiles() == [expected_profile_name]
