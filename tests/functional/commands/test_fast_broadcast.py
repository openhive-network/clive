from __future__ import annotations

from typing import TYPE_CHECKING

from clive.models.asset import Asset
from clive.models.transfer_operation import TransferOperation

if TYPE_CHECKING:
    import clive
    from clive.__private.storage.mock_database import PrivateKeyAlias


def test_fast_broadcast_smoke_test(world: clive.World, pubkey: PrivateKeyAlias) -> None:
    # ARRANGE, ACT & ASSERT
    world.commands.fast_broadcast(
        operation=TransferOperation(
            from_="initminer", to="alice", amount=Asset.hive(1), memo="aaaaa"
        ),
        sign_with=pubkey,
    )
