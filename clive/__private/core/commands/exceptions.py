from __future__ import annotations

from clive.__private.core.commands.abc.command import Command, CommandError


class MultipleWalletsUnlockedError(CommandError):
    def __init__(self, command: Command) -> None:
        super().__init__(command, "Beekeeper session must be unlocked for at most one profile.")


class ProfileNotUnlockedError(CommandError):
    def __init__(self, command: Command) -> None:
        super().__init__(command, "Beekeeper session must be unlocked for one profile.")


class WalletNotFoundError(CommandError):
    def __init__(self, command: Command, wallet_name: str) -> None:
        super().__init__(command, f"Wallet `{wallet_name}` not found on the beekeeper.")
