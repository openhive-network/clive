from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.encryption import EncryptionService

if TYPE_CHECKING:
    from beekeepy import AsyncSession, AsyncUnlockedWallet

    from clive.__private.core.app_state import AppState


@dataclass
class CreateWalletResult:
    unlocked_wallet: AsyncUnlockedWallet
    unlocked_profile_encryption_wallet: AsyncUnlockedWallet
    password: str
    is_password_generated: bool
    """Will be set if was generated because no password was provided when creating wallet."""


@dataclass(kw_only=True)
class CreateWallet(CommandWithResult[CreateWalletResult]):
    app_state: AppState | None = None
    session: AsyncSession
    wallet_name: str
    password: str | None

    async def _execute(self) -> None:
        result = await self.session.create_wallet(name=self.wallet_name, password=self.password)
        if isinstance(result, tuple):
            unlocked_wallet, password = result
            is_password_generated = True
        else:
            unlocked_wallet = result
            assert self.password is not None, "When no password is generated, it means it was provided."
            password = self.password
            is_password_generated = False

        unlocked_profile_encryption_wallet = await self.session.create_wallet(
            name=EncryptionService.get_encryption_wallet_name(self.wallet_name), password=password
        )
        await unlocked_profile_encryption_wallet.generate_key()
        self._result = CreateWalletResult(
            unlocked_wallet=unlocked_wallet,
            unlocked_profile_encryption_wallet=unlocked_profile_encryption_wallet,
            password=password,
            is_password_generated=is_password_generated,
        )

        if self.app_state:
            await self.app_state.unlock((unlocked_wallet, unlocked_profile_encryption_wallet))
