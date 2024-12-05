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
        super().__init__(command, "There is no unlocked profile the beekeeper.")
