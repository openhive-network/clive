from __future__ import annotations

from typing import Final

from clive.__private.core.commands.abc.command import Command, CommandError


class MultipleProfilesUnlockedError(CommandError):
    def __init__(self, command: Command) -> None:
        super().__init__(command, "Multiple profiles are unlocked on the beekeeper.")


class NoProfileUnlockedError(CommandError):
    def __init__(self, command: Command) -> None:
        super().__init__(command, "There is no unlocked profile on the beekeeper.")


class MultipleEncryptionWalletsUnlockedError(CommandError):
    MESSAGE: Final[str] = "Multiple encryption wallets are unlocked on the beekeeper. There should be only one."

    def __init__(self, command: Command) -> None:
        super().__init__(command, self.MESSAGE)


class NoEncryptionWalletUnlockedError(CommandError):
    MESSAGE: Final[str] = "There is no unlocked encryption wallet on the beekeeper. There should be only one."

    def __init__(self, command: Command) -> None:
        super().__init__(command, self.MESSAGE)
