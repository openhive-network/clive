from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive.__private.core.world import World

if TYPE_CHECKING:
    from collections.abc import Iterator

    from clive.__private.core.beekeeper import Beekeeper


@pytest.fixture
def world(wallet_name: str, beekeeper: Beekeeper) -> Iterator[World]:
    w = World(profile_name=wallet_name)
    # TODO: instead of reopening, pass argument through Dynaconf
    w._debug_replace_beekeeper(beekeeper)
    yield w
    w.close()
