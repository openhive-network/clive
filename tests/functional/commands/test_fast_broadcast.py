from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.models import Asset
from schemas.operations import TransferOperation

if TYPE_CHECKING:
    import test_tools as tt

    from clive.__private.core.world import World
    from clive_local_tools.models import WalletInfo


async def test_fast_broadcast_smoke_test(
    world: World, init_node: tt.InitNode, wallet: WalletInfo  # noqa: ARG001
) -> None:
    # ARRANGE
    pubkey = (
        await world.commands.import_key(
            key_to_import=PrivateKeyAliased(value=str(init_node.config.private_key[0]), alias="some-alias")
        )
    ).result_or_raise

    # ACT & ASSERT
    await world.commands.fast_broadcast(
        operation=TransferOperation(from_="initminer", to="null", amount=Asset.hive(1), memo=""),
        sign_with=pubkey,
    )
