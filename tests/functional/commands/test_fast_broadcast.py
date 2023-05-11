from __future__ import annotations

from typing import TYPE_CHECKING

from clive.models.transfer_operation import TransferOperation

if TYPE_CHECKING:
    from clive.__private.storage.mock_database import PrivateKeyAlias
    from tests.conftest import WorldWithNodeT


def test_fast_broadcast_smoke_test(world_with_node: WorldWithNodeT, pubkey: PrivateKeyAlias) -> None:
    # ARRANGE
    amount = {
        "amount": 1,
        "precision": 3,
        "nai": "@@000000013",
    }

    world, node = world_with_node

    # ACT & ASSERT
    world.commands.fast_broadcast(
        operation=TransferOperation(from_="initminer", to="alice", amount=amount, memo=""),
        sign_with=pubkey,
    )
