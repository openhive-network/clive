from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.storage.service import PersistentStorageService

if TYPE_CHECKING:
    from clive.__private.core.world import World


async def test_if_profile_is_saved(world: World, wallet_name: str) -> None:
    await PersistentStorageService(world.beekeeper).save_profile(world.profile)

    # ARRANGE, ACT & ASSERT
    assert PersistentStorageService.list_stored_profile_names() == [wallet_name]
