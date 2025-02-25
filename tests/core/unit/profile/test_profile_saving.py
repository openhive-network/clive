from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clive.__private.core.world import World


async def test_if_profile_is_saved(world: World, prepare_profile_with_wallet: None, wallet_name: str) -> None:  # noqa: ARG001
    # ACT
    await world.commands.save_profile()

    # ASSERT
    actual_profiles = world.profile.list_profiles()
    assert actual_profiles == [wallet_name], f"Actual profiles are {actual_profiles}, expected are {[wallet_name]}"
