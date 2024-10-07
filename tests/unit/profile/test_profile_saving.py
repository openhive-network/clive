from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.encryption import EncryptionService
from clive.__private.storage.service import PersistentStorageService

if TYPE_CHECKING:
    from clive.__private.core.profile import Profile
    from clive.__private.core.world import World


async def test_if_profile_is_saved(world: World, prepare_profile_with_session: Profile) -> None:
    encryption_service = await EncryptionService.from_beekeeper(world.beekeeper)
    await world.profile.save(encryption_service)

    # ARRANGE, ACT & ASSERT
    assert PersistentStorageService.list_stored_profile_names() == [prepare_profile_with_session.name]
