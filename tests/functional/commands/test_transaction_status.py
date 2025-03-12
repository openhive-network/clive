from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from beekeepy.exceptions import ApiNotFoundError

from clive.__private.core.keys import PrivateKeyAliased
from clive.__private.logger import logger
from clive.__private.models import Asset
from clive.__private.models.schemas import TransferOperation


if TYPE_CHECKING:
    import test_tools as tt

    from clive.__private.core.world import World


async def test_transaction_status_in_blockchain(
    world: World,
    init_node_extra_apis: tt.InitNode,
    prepare_profile_with_wallet: None,  # noqa: ARG001
) -> None:
    # ARRANGE
    pubkey = (
        await world.commands.import_key(
            key_to_import=PrivateKeyAliased(value=str(init_node_extra_apis.config.private_key[0]), alias="some-alias")
        )
    ).result_or_raise
    operation = TransferOperation(from_="initminer", to="null", amount=Asset.hive(2), memo="for testing")
    transaction = (
        await world.commands.perform_actions_on_transaction(content=operation, sign_key=pubkey, broadcast=True)
    ).result_or_raise
    init_node_extra_apis.wait_number_of_blocks(1)

    transaction_id = transaction.with_hash().transaction_id

    # ACT
    result = (await world.commands.find_transaction(transaction_id=transaction_id)).result_or_raise
    logger.info(f"{result}")

    # ASSERT
    assert "reversible" in result.status


async def test_transaction_status_unknown(world: World, init_node_extra_apis: tt.InitNode) -> None:
    # ACT
    result = (await world.commands.find_transaction(transaction_id="deadbeef")).result_or_raise
    logger.info(f"{result}")

    # ASSERT
    assert "unknown" in result.status


async def test_transaction_status_no_api(world: World, init_node: tt.InitNode) -> None:
    # ARRANGE
    expected_message = "Could not find API transaction_status_api"
    assert "transaction_status_api" not in init_node.config.plugin

    # ACT & ASSERT
    with pytest.raises(ApiNotFoundError) as exc_info:
        await world.commands.find_transaction(transaction_id="deadbeef")

    assert expected_message in str(exc_info.value.response), "Got different error message than expected"
