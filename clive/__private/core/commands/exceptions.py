from __future__ import annotations

from clive.__private.core.commands.abc.command import Command, CommandError


class WalletNotFoundError(CommandError):
    def __init__(self, command: Command, wallet_name: str) -> None:
        super().__init__(command, f"Wallet `{wallet_name}` not found on the beekeeper.")


class MultipleProfilesUnlockedError(CommandError):
    def __init__(self, command: Command) -> None:
        super().__init__(command, "Multiple profiles are unlocked on the beekeeper.")


class NoProfileUnlockedError(CommandError):
    def __init__(self, command: Command) -> None:
        super().__init__(command, "There is no unlocked profile on the beekeeper.")


class ProfileEncryptionKeyError(CommandError):
    def __init__(self, command: Command, number_of_keys: int) -> None:
        message = f"Error retrieving profile encryption keys. Number of keys: {number_of_keys}."
        super().__init__(command, message)
