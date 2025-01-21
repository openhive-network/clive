from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar, Protocol

from clive.__private.core.commands.abc.command_restricted import CommandExecutionNotPossibleError, CommandRestricted

if TYPE_CHECKING:
    from beekeepy import AsyncUnlockedWallet, AsyncWallet


class AppStateProtocol(Protocol):
    @property
    async def is_unlocked(self) -> bool: ...


class CommandRequiresUnlockedModeError(CommandExecutionNotPossibleError):
    def __init__(self, command: CommandInUnlocked) -> None:
        super().__init__(command, reason="requires the application to be in unlocked mode.")


class CommandRequiresUnlockedWalletToBeSetError(CommandExecutionNotPossibleError):
    def __init__(self, command: CommandInUnlocked) -> None:
        super().__init__(command, reason="_is_execution_possible was skipped and self.__unlocked_wallet was not set")


@dataclass(kw_only=True)
class CommandInUnlocked(CommandRestricted, ABC):
    """A command that require the application to be in unlocked mode."""

    wallet: AsyncUnlockedWallet | AsyncWallet

    __unlocked_wallet: AsyncUnlockedWallet | None = field(default=None, init=False)
    _execution_impossible_error: ClassVar[type[CommandExecutionNotPossibleError]] = CommandRequiresUnlockedModeError

    @property
    def unlocked_wallet(self) -> AsyncUnlockedWallet:
        if self.__unlocked_wallet is None:
            raise CommandRequiresUnlockedWalletToBeSetError(self)
        return self.__unlocked_wallet

    async def _is_execution_possible(self) -> bool:
        self.__unlocked_wallet = await self.wallet.unlocked
        return self.__unlocked_wallet is not None
