from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import pytest

from clive.__private.core.node.node import NothingToSendError, ResponseNotReadyError
from clive.exceptions import CommunicationError

if TYPE_CHECKING:
    import test_tools as tt

    from clive.__private.core.profile import Profile
    from clive.__private.core.world import World


async def test_batch_node(init_node: tt.InitNode, world: World) -> None:  # noqa: ARG001
    async with world.node.batch() as node:
        dynamic_properties = await node.api.database_api.get_dynamic_global_properties()
        config = await node.api.database_api.get_config()

    assert len(dynamic_properties.dict(by_alias=True)) != 0
    assert len(config.dict(by_alias=True)) != 0


async def test_batch_node_response_not_ready(init_node: tt.InitNode, world: World) -> None:  # noqa: ARG001
    async with world.node.batch() as node:
        dynamic_properties = await node.api.database_api.get_dynamic_global_properties()

        with pytest.raises(ResponseNotReadyError):
            _ = dynamic_properties.head_block_id


async def test_batch_node_error_response(init_node: tt.InitNode, world: World) -> None:  # noqa: ARG001
    with pytest.raises(CommunicationError, match="Invalid cast"):
        async with world.node.batch() as node:
            await node.api.database_api.find_accounts(accounts=123)  # type: ignore[arg-type]


async def test_batch_node_error_response_delayed(init_node: tt.InitNode, world: World) -> None:  # noqa: ARG001
    async with world.node.batch(delay_error_on_data_access=True) as node:
        response = await node.api.database_api.find_accounts(accounts=123)  # type: ignore[arg-type]

    with pytest.raises(CommunicationError, match="Invalid cast"):
        _ = response.accounts[0].name


@pytest.mark.parametrize("order", ["first_good", "first_bad"])
async def test_batch_node_mixed_request_delayed(
    init_node: tt.InitNode,  # noqa: ARG001
    world: World,
    order: Literal["first_good", "first_bad"],
) -> None:
    async with world.node.batch(delay_error_on_data_access=True) as node:
        if order == "first_good":
            good_response = await node.api.database_api.get_dynamic_global_properties()
            bad_response = await node.api.database_api.find_accounts(accounts=123)  # type: ignore[arg-type]
        else:
            bad_response = await node.api.database_api.find_accounts(accounts=123)  # type: ignore[arg-type]
            good_response = await node.api.database_api.get_dynamic_global_properties()

    assert good_response.head_block_number > 0
    with pytest.raises(CommunicationError, match="Invalid cast"):
        _ = bad_response.accounts[0].name


async def test_batch_node_nothing_to_send(world: World, prepare_profile_with_wallet: Profile) -> None:  # noqa: ARG001
    with pytest.raises(NothingToSendError):
        async with world.node.batch():
            pass
