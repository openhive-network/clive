from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from beekeepy.exceptions import CommunicationError

from clive.__private.core.beekeeper_manager import WalletsNotAvailableError
from clive.__private.core.commands.abc.command import Command, CommandError
from clive.__private.core.commands.abc.command_encryption import CommandEncryption
from clive.__private.core.encryption import EncryptionService
from clive.__private.core.wallet_container import WalletContainer

if TYPE_CHECKING:
    from clive.__private.core.profile import Profile


class ProfileSavingFailedError(CommandError):
    MESSAGE: Final[str] = "Profile saving failed because beekeeper is not available."

    def __init__(self, command: Command) -> None:
        super().__init__(command, self.MESSAGE)


@dataclass(kw_only=True)
class SaveProfile(CommandEncryption, Command):
    profile: Profile

    @property
    def _should_skip_execution(self) -> bool:
        return self.profile.is_skip_save_set

    async def _execute(self) -> None:
        encryption_service = EncryptionService(WalletContainer(self.unlocked_wallet, self.unlocked_encryption_wallet))
        try:
            await self.profile.save(encryption_service)
        except (CommunicationError, WalletsNotAvailableError) as error:
            raise ProfileSavingFailedError(self) from error
