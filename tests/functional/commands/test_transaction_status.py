from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.logger import logger
from clive.exceptions import CommunicationError
from clive.models import Asset
from schemas.operations import TransferOperation

if TYPE_CHECKING:
    import test_tools as tt

    from clive.__private.core.world import World
    from tests import WalletInfo


async def test_transaction_status_in_blockchain(
    world: World, init_node_extra_apis: tt.InitNode, wallet: WalletInfo  # noqa: ARG001
) -> None:
    # ARRANGE
    pubkey = (
        await world.commands.import_key(
            key_to_import=PrivateKeyAliased(value=str(init_node_extra_apis.config.private_key[0]), alias="some-alias")
        )
    ).result_or_raise

    operation = TransferOperation(from_="initminer", to="null", amount=Asset.hive(2), memo="for testing")
    transaction_without_signature = (await world.commands.build_transaction(operations=[operation])).result_or_raise
    transaction = (
        await world.commands.sign(
            transaction=transaction_without_signature,
            sign_with=pubkey,
        )
    ).result_or_raise

    await world.commands.broadcast(transaction=transaction)
    init_node_extra_apis.wait_number_of_blocks(1)

    response = init_node_extra_apis.api.account_history.get_account_history(
        account="null",
        start=-1,
        limit=1,
        include_reversible=True,
        operation_filter_low=0xFFFFFFFFFFFFFFFF,
        operation_filter_high=0,
    )
    account_history_operation = response["history"][0]
    transaction_id = account_history_operation[1]["trx_id"]

    # ACT & ASSERT
    status = await world.commands.find_transaction(transaction_id=transaction_id)
    result = status.result_or_raise
    logger.info(f"{result}")
    assert "reversible" in result.status


async def test_transaction_status_unknown(world: World, init_node_extra_apis: tt.InitNode) -> None:  # noqa: ARG001
    # ACT & ASSERT
    status = await world.commands.find_transaction(transaction_id="deadbeef")
    result = status.result_or_raise
    logger.info(f"{result}")
    assert "unknown" in result.status


async def test_transaction_status_no_api(world: World, init_node: tt.InitNode) -> None:  # noqa: ARG001
    # ACT & ASSERT
    with pytest.raises(CommunicationError):
        await world.commands.find_transaction(transaction_id="deadbeef")
