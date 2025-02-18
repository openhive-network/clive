from __future__ import annotations

from typing import TYPE_CHECKING, Final

from clive.exceptions import CliveError

if TYPE_CHECKING:
    from beekeepy import AsyncSession, AsyncUnlockedWallet

    from clive.__private.core.wallet_container import WalletContainer


class WalletsNotAvailableError(CliveError):
    MESSAGE: Final[str] = "Wallets are not available. They should be available when application is unlocked."

    def __init__(self) -> None:
        super().__init__(self.MESSAGE)


class WalletManager:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._wallets: WalletContainer | None = None

    def __bool__(self) -> bool:
        return bool(self._wallets)

    @property
    def user_wallet(self) -> AsyncUnlockedWallet:
        return self._content.user_wallet

    @property
    def encryption_wallet(self) -> AsyncUnlockedWallet:
        return self._content.encryption_wallet

    @property
    def name(self) -> str:
        return self._content.name

    @property
    def _content(self) -> WalletContainer:
        if not self._wallets:
            raise WalletsNotAvailableError
        return self._wallets

    async def set_wallets(self, wallets: WalletContainer) -> None:
        existing_wallet_names = [wallet.name for wallet in (await self._session.wallets)]

        def assert_wallet_exists(name: str) -> None:
            assert name in existing_wallet_names, f"Wallet {name} does not exists within this session"

        assert_wallet_exists(wallets.user_wallet.name)
        assert_wallet_exists(wallets.encryption_wallet.name)

        self._wallets = wallets
