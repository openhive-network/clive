from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from beekeepy.settings import RemoteHandleSettings

from clive.__private.core.commands.data_retrieval.async_hived.async_handle import AsyncHived

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    import test_tools as tt


@pytest.fixture
async def async_node(init_node: tt.InitNode) -> AsyncIterator[AsyncHived]:
    settings = RemoteHandleSettings(http_endpoint=init_node.http_endpoint)
    async with AsyncHived(settings=settings) as hived:
        yield hived
