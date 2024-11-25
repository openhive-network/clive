from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from beekeepy import AsyncBeekeeper


async def assert_wallets_locked(beekeeper: AsyncBeekeeper) -> None:
    wallets = await (await beekeeper.session).wallets
    assert all(w.unlocked is None for w in wallets), "All wallets should be locked."


async def assert_wallet_unlocked(beekeeper: AsyncBeekeeper, wallet_name: str) -> None:
    wallets = await (await beekeeper.session).wallets
    assert any(
        (w.name == wallet_name) and (w.unlocked is not None) for w in wallets
    ), f"Wallet {wallet_name} should be unlocked."
