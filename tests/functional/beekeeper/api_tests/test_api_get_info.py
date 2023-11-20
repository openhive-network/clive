from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from clive.__private.core.beekeeper.defaults import BeekeeperDefaults

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper


async def test_api_get_info(beekeeper: Beekeeper) -> None:
    """Test test_api_get_info will test beekeeper_api.get_info api call."""
    # ARRANGE & ACT
    get_info = await beekeeper.api.get_info()

    # ASSERT
    assert get_info.now + timedelta(seconds=BeekeeperDefaults.DEFAULT_UNLOCK_TIMEOUT) == get_info.timeout_time
