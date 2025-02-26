from __future__ import annotations

from typing import TYPE_CHECKING, Final

from beekeepy import AsyncBeekeeper, AsyncSession
from beekeepy import Settings as BeekeepySettings

from clive.__private.settings import safe_settings
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from beekeepy import AsyncSession, AsyncUnlockedWallet

    from clive.__private.core.wallet_container import WalletContainer


class WalletsNotAvailableError(CliveError):
    MESSAGE: Final[str] = "Wallets are not available. They should be available when application is unlocked."

    def __init__(self) -> None:
        super().__init__(self.MESSAGE)


class BeekeeperManager:
    def __init__(self) -> None:
        self._beekeeper_settings = self._setup_beekeepy_settings()
        self._beekeeper: AsyncBeekeeper | None = None
        self._session: AsyncSession | None = None
        self._wallets: WalletContainer | None = None

    async def setup_beekeeper(self) -> None:
        self._beekeeper = await self._setup_beekeeper()
        self._session = await self.beekeeper.session

    def teardown(self) -> None:
        if self._beekeeper is not None:
            self._beekeeper.teardown()
        self._beekeeper = None
        self._session = None
        self.clear_wallets()

    def __bool__(self) -> bool:
        return bool(self._wallets)

    @property
    def beekeeper_settings(self) -> BeekeepySettings:
        return self._beekeeper_settings

    @property
    def beekeeper(self) -> AsyncBeekeeper:
        message = "Beekeeper is not available. Did you forget to use as a context manager or call `setup`?"
        assert self._beekeeper is not None, message
        return self._beekeeper

    @property
    def session(self) -> AsyncSession:
        message = "Session is not available. Did you forget to use as a context manager or call `setup`?"
        assert self._session is not None, message
        return self._session

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
        existing_wallet_names = [wallet.name for wallet in (await self.session.wallets)]

        def assert_wallet_exists(name: str) -> None:
            assert name in existing_wallet_names, f"Wallet {name} does not exists within this session"

        assert_wallet_exists(wallets.user_wallet.name)
        assert_wallet_exists(wallets.encryption_wallet.name)

        self._wallets = wallets

    def clear_wallets(self) -> None:
        self._wallets = None

    def _setup_beekeepy_settings(self) -> BeekeepySettings:
        return safe_settings.beekeeper.settings_factory()

    async def _setup_beekeeper(self) -> AsyncBeekeeper:
        if self.beekeeper_settings.http_endpoint is not None:
            return await AsyncBeekeeper.remote_factory(url_or_settings=self.beekeeper_settings)

        return await AsyncBeekeeper.factory(settings=self.beekeeper_settings)
