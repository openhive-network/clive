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
        super().__init__(command, "Multiple profile encryption wallets are unlocked on the beekeeper.")


class NoEncryptionWalletUnlockedError(CommandError):
    def __init__(self, command: Command) -> None:
        super().__init__(command, "There is no unlocked profile encryption wallet on the beekeeper.")


class ProfileEncryptionKeyAmountError(CommandError):
    def __init__(self, command: Command, number_of_keys: int) -> None:
        message = (
            f"Error retrieving profile encryption key. Number of keys: {number_of_keys}."
            " There should be one and only one key."
        )
        super().__init__(command, message)


class CommandDecryptError(CommandError):
    def __init__(self, command: Command) -> None:
        super().__init__(command)


class CommandEncryptError(CommandError):
    def __init__(self, command: Command) -> None:
        super().__init__(command)
