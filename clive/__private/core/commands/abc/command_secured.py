from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import ClassVar

from clive.__private.core.commands.abc.command import Command
from clive.exceptions import CommunicationError, KnownError


class InvalidPasswordError(KnownError):
    ERROR_MESSAGE: ClassVar[str] = "Invalid password for wallet: "


@dataclass(kw_only=True)
class CommandPasswordSecured(Command, ABC):
    """A command that requires a password to proceed."""

    password: str

    async def execute(self) -> None:
        try:
            await super().execute()
        except CommunicationError as error:
            if InvalidPasswordError.ERROR_MESSAGE in str(error):
                raise InvalidPasswordError(f"Command {self.__class__.__name__} received wrong password.") from error
            raise
