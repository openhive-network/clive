from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from beekeepy import AsyncBeekeeper


async def assert_wallets_locked(beekeeper: AsyncBeekeeper) -> None:
    wallets = await (await beekeeper.session).wallets
    locked_wallets = [(await w.unlocked) is None for w in wallets]
    assert all(locked_wallets), "All wallets should be locked."


async def assert_wallet_unlocked(beekeeper: AsyncBeekeeper, wallet_name: str) -> None:
    wallets = await (await beekeeper.session).wallets
    unlocked_wallets = [((wallet.name == wallet_name) and ((await wallet.unlocked) is not None)) for wallet in wallets]
    assert any(unlocked_wallets), f"Wallet {wallet_name} should be unlocked."
