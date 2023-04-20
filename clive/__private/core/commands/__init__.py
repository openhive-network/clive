from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from clive.__private.core.commands.command import Command

T = TypeVar("T")
def execute_with_result(command: Command[T]) -> T:
    command.execute()
    return command.result
