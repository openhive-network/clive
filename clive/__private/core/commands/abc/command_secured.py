from __future__ import annotations

from abc import ABC
from dataclasses import dataclass

from clive.__private.core.commands.abc.command import Command


@dataclass(kw_only=True)
class CommandPasswordSecured(Command, ABC):
    """
    A command that requires a password to proceed.

    In case the password is invalid, there could be `beekeepy.exceptions.InvalidPasswordError` raised.

    Attributes:
        password: The password required to execute the command.
    """

    password: str
