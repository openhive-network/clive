from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive.__private.core.node.node import ResponseNotReadyError
from clive.exceptions import CommunicationError

if TYPE_CHECKING:
    import test_tools as tt

    from clive.__private.core.world import World


async def test_batch_node(init_node: tt.InitNode, world: World) -> None:  # noqa: ARG001
    async with world.node.batch() as node:
        dynamic_properties = await node.api.database_api.get_dynamic_global_properties()
        config = await node.api.database_api.get_config()

    assert len(dynamic_properties.dict(by_alias=True)) != 0
    assert len(config.dict(by_alias=True)) != 0


async def test_false_batch_node(init_node: tt.InitNode, world: World) -> None:  # noqa: ARG001
    async with world.node.batch() as node:
        dynamic_properties = await node.api.database_api.get_dynamic_global_properties()

        with pytest.raises(ResponseNotReadyError):
            _ = dynamic_properties.head_block_id


async def test_false_batch_node_error_response(init_node: tt.InitNode, world: World) -> None:  # noqa: ARG001
    with pytest.raises(CommunicationError):  # noqa: PT012
        async with world.node.batch() as node:
            _ = await node.api.database_api.find_accounts(accounts=123)  # type: ignore
