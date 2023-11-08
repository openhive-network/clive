from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

import wax
from clive.__private.core.keys import PrivateKeyAliased
from clive.__private.core.perform_actions_on_transaction import perform_actions_on_transaction
from clive.models import Asset
from schemas.operations import TransferOperation

from .consts import ENCODING, VALID_TRX_ID_WITH_TRANSACTIONS

if TYPE_CHECKING:
    import test_tools as tt

    from clive.__private.core.world import World
    from tests import WalletInfo


@pytest.mark.parametrize("trx_id", list(VALID_TRX_ID_WITH_TRANSACTIONS))
def test_proper_transaction_id(trx_id: str) -> None:
    result = wax.calculate_transaction_id(VALID_TRX_ID_WITH_TRANSACTIONS[trx_id].encode(ENCODING))
    assert result.status == wax.python_error_code.ok
    assert not result.exception_message
    assert result.result.decode(ENCODING) == trx_id


async def test_transaction_id_is_the_same_as_in_account_history_api(
    world: World, init_node_extra_apis: tt.InitNode, wallet: WalletInfo  # noqa: ARG001
) -> None:
    # ARRANGE
    pubkey = (
        await world.commands.import_key(
            key_to_import=PrivateKeyAliased(value=str(init_node_extra_apis.config.private_key[0]), alias="some-alias")
        )
    ).result_or_raise

    operation = TransferOperation(from_="initminer", to="null", amount=Asset.hive(2), memo="for testing")

    transaction = await perform_actions_on_transaction(
        content=operation,
        app_state=world.app_state,
        beekeeper=world.beekeeper,
        node=world.node,
        chain_id=await world.node.chain_id,
        sign_key=pubkey,
        broadcast=True,
    )

    init_node_extra_apis.wait_number_of_blocks(1)

    # ACT
    response = init_node_extra_apis.api.account_history.get_account_history(
        account="null",
        start=-1,
        limit=1,
        include_reversible=True,
        operation_filter_low=0xFFFFFFFFFFFFFFFF,
        operation_filter_high=0,
    )
    account_history_operation = response["history"][0]
    transaction_id_from_api = account_history_operation[1]["trx_id"]

    transaction_id_from_wax = transaction.calculate_transaction_id()

    # ASSERT
    assert (
        transaction_id_from_api == transaction_id_from_wax
    ), "transaction_id_from_api is not equal to transaction_id_from_wax"
