from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from beekeepy.exceptions import CommunicationError

if TYPE_CHECKING:
    from clive.__private.core.node.async_hived.async_handle import AsyncHived


async def test_async_batch_node(async_node: AsyncHived) -> None:
    # ACT
    async with await async_node.batch() as node:
        dynamic_properties = await node.api.database.get_dynamic_global_properties()
        config = await node.api.database.get_config()

    # ASSERT
    assert dynamic_properties.dict(), "Dynamic global properties should not be empty"
    assert config.dict(), "Config should not be empty"
    assert dynamic_properties.head_block_number > 0, "Head block number should be higher than 0"


async def test_async_batch_node_error_response(async_node: AsyncHived) -> None:
    # ACT & ASSERT
    with pytest.raises(CommunicationError, match="Invalid cast"):
        async with await async_node.batch() as node:
            await node.api.database.find_accounts(accounts=123)


async def test_async_batch_node_error_response_delayed(async_node: AsyncHived) -> None:
    # ACT
    async with await async_node.batch(delay_error_on_data_access=True) as node:
        response = await node.api.database.find_accounts(accounts=123)

    # ASSERT
    with pytest.raises(CommunicationError, match="Invalid cast"):
        _ = response.accounts[0].name
