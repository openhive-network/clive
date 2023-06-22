from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.keys.keys import PrivateKey
from clive.models import Asset
from schemas.operations import TransferOperation

if TYPE_CHECKING:
    import test_tools as tt

    from clive.__private.core.world import World
    from tests import WalletInfo


def test_fast_broadcast_smoke_test(world: World, init_node: tt.InitNode, wallet: WalletInfo) -> None:  # noqa: ARG001
    # ARRANGE
    pubkey = world.commands.import_key(alias="some-alias", wif=PrivateKey(value=str(init_node.config.private_key[0])))

    # ACT & ASSERT
    world.commands.fast_broadcast(
        operation=TransferOperation(from_="initminer", to="null", amount=Asset.hive(1), memo=""),
        sign_with=pubkey,
    )
