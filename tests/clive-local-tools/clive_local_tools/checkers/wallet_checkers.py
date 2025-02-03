from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.commands.is_wallet_unlocked import IsWalletUnlocked

if TYPE_CHECKING:
    from beekeepy import AsyncBeekeeper


async def assert_wallets_locked(beekeeper: AsyncBeekeeper) -> None:
    wallets = await (await beekeeper.session).wallets
    locked_wallets = [not await IsWalletUnlocked(wallet=wallet).execute_with_result() for wallet in wallets]
    assert all(locked_wallets), "All wallets should be locked."


async def assert_wallet_unlocked(beekeeper: AsyncBeekeeper, wallet_name: str) -> None:
    unlocked_wallets = await (await beekeeper.session).wallets_unlocked
    unlocked_wallet_names = [wallet.name for wallet in unlocked_wallets]
    assert wallet_name in unlocked_wallet_names, f"Wallet `{wallet_name}` should be unlocked."
