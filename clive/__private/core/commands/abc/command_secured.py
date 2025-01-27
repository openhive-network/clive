from __future__ import annotations

from abc import ABC
from dataclasses import dataclass

from clive.__private.core.commands.abc.command import Command


@dataclass(kw_only=True)
class CommandPasswordSecured(Command, ABC):
    """A command that requires a password to proceed."""

    password: str
