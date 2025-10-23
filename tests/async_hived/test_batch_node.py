from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from beekeepy.exceptions import CommunicationError
from msgspec import ValidationError  # TODO: new msgspec refactor should encapsulate schemas !!!

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.async_hived.async_handle import AsyncHived


async def test_async_batch_node(async_node: AsyncHived) -> None:
    try:
        async with await async_node.batch() as node:
            dynamic_properties = await node.api.database.get_dynamic_global_properties()
            config = await node.api.database.get_config()

        assert len(dynamic_properties.dict()) != 0, "Dynamic global properties should not be empty"
        assert len(config.dict()) != 0, "Config should not be empty"
    except ValidationError as ex:
        repr(ex).index("Object missing required field `HIVE_CUSTOM_OP_BLOCK_LIMIT")


async def test_async_batch_node_error_response_delayed(async_node: AsyncHived) -> None:
    async with await async_node.batch(delay_error_on_data_access=True) as node:
        response = await node.api.database.find_accounts(accounts=123)

    with pytest.raises(CommunicationError, match="Invalid cast"):
        _ = response.accounts[0].name
