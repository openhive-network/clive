from __future__ import annotations

from clive.__private.core.commands.abc.command import Command, CommandError


class MultipleProfilesUnlockedError(CommandError):
    def __init__(self, command: Command) -> None:
        super().__init__(command, "Multiple profiles are unlocked on the beekeeper.")


class NoProfileUnlockedError(CommandError):
    def __init__(self, command: Command) -> None:
        super().__init__(command, "There is no unlocked profile on the beekeeper.")


class MultipleEncryptionWalletsUnlockedError(CommandError):
    def __init__(self, command: Command) -> None:
        super().__init__(
            command, "Multiple encryption wallets are unlocked on the beekeeper. There should be only one."
        )


class NoEncryptionWalletUnlockedError(CommandError):
    def __init__(self, command: Command) -> None:
        super().__init__(command, "There is no unlocked encryption wallet on the beekeeper. There should be only one.")


class EncryptionKeyAmountError(CommandError):
    def __init__(self, command: Command, number_of_keys: int) -> None:
        message = (
            f"Error retrieving encryption key. Number of keys: {number_of_keys}."
            " There should be one and only one key."
        )
        super().__init__(command, message)
