from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from clive.__private.core.commands.abc.command_restricted import CommandExecutionNotPossibleError, CommandRestricted
from clive.__private.core.commands.is_wallet_unlocked import IsWalletUnlocked

if TYPE_CHECKING:
    from beekeepy import AsyncUnlockedWallet


class CommandRequiresUnlockedModeError(CommandExecutionNotPossibleError):
    def __init__(self, command: CommandInUnlocked) -> None:
        super().__init__(command, reason="requires the application to be in unlocked mode.")


@dataclass(kw_only=True)
class CommandInUnlocked(CommandRestricted, ABC):
    """
    A command that require the application to be in unlocked mode.

    Attributes:
        unlocked_wallet: The unlocked wallet to use for the command.
    """

    unlocked_wallet: AsyncUnlockedWallet

    _execution_impossible_error: ClassVar[type[CommandExecutionNotPossibleError]] = CommandRequiresUnlockedModeError

    async def _is_execution_possible(self) -> bool:
        return await IsWalletUnlocked(wallet=self.unlocked_wallet).execute_with_result()
