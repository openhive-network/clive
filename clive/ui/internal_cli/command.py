from __future__ import annotations

from enum import Enum
from typing import Any, Callable, Sequence


class CommandMode(Enum):
    """The mode in which a command can be executed."""

    ACTIVE = "auto"
    INACTIVE = "inactive"
    BOTH = "both"


class Command:
    def __init__(
        self,
        name: str,
        *,
        help_: str,
        handler: Callable[..., Any] | None,
        mode: CommandMode,
        children: Sequence[Command] | None = None,
    ) -> None:
        self.__name = name
        self.__handler = handler
        self.__help = help_
        self.__mode = mode
        self.__children = children or []

    @property
    def name(self) -> str:
        return self.__name

    @property
    def help(self) -> str:
        return self.__help

    @property
    def mode(self) -> CommandMode:
        return self.__mode

    @property
    def children(self) -> Sequence[Command]:
        return self.__children
