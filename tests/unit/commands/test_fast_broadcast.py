from __future__ import annotations

from typing import TYPE_CHECKING

from clive.models.transfer_operation import TransferOperation

if TYPE_CHECKING:
    import clive
    from tests import WalletInfo


def test_fast_broadcast_smoke_test(world: clive.World, wallet: WalletInfo) -> None:
    # ARRANGE, ACT & ASSERT
    world.commands.fast_broadcast(
        operation=TransferOperation(from_="initminer", to="alice", amount="1.000", asset="HIVE"), sign_with=wallet.pub
    )
