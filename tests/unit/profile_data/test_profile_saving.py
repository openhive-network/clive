from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clive.__private.core.world import World


def test_if_profile_is_saved(world: World, wallet_name: str) -> None:
    world.profile_data.save()

    # ARRANGE, ACT & ASSERT
    assert world.profile_data.list_profiles() == [wallet_name]
