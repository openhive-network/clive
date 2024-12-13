from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clive.__private.core.world import World


def test_if_profile_is_saved(world: World, prepare_profile_with_wallet: None, wallet_name: str) -> None:  # noqa: ARG001
    # ACT
    world.profile.save()

    # ASSERT
    assert world.profile.list_profiles() == [wallet_name]
