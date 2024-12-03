from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper


async def assert_wallets_locked(beekeeper: Beekeeper) -> None:
    wallets = (await beekeeper.api.list_wallets()).wallets
    assert all(not w.unlocked for w in wallets), "All wallets should be locked."


async def assert_wallet_unlocked(beekeeper: Beekeeper, wallet_name: str) -> None:
    wallets = (await beekeeper.api.list_wallets()).wallets
    assert any(w.name == wallet_name and w.unlocked for w in wallets), f"Wallet {wallet_name} should be unlocked."
