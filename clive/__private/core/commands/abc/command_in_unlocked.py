from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Protocol

from clive.__private.core.commands.abc.command_restricted import CommandExecutionNotPossibleError, CommandRestricted

if TYPE_CHECKING:
    from beekeepy import AsyncUnlockedWallet


class AppStateProtocol(Protocol):
    @property
    async def is_unlocked(self) -> bool: ...


class CommandRequiresUnlockedModeError(CommandExecutionNotPossibleError):
    def __init__(self, command: CommandInUnlocked) -> None:
        super().__init__(command, reason="requires the application to be in unlocked mode.")


@dataclass(kw_only=True)
class CommandInUnlocked(CommandRestricted, ABC):
    """A command that require the application to be in unlocked mode."""

    unlocked_wallet: AsyncUnlockedWallet

    _execution_impossible_error: ClassVar[type[CommandExecutionNotPossibleError]] = CommandRequiresUnlockedModeError

    async def _is_execution_possible(self) -> bool:
        is_wallet_unlocked = await self.unlocked_wallet.unlocked is not None
        return is_wallet_unlocked  # noqa: RET504
