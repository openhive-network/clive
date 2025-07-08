from __future__ import annotations

from typing import TypeGuard

from clive.__private.core.commands.abc.command import CommandError
from clive.__private.core.error_handlers.abc.error_notificator import ErrorNotificator


class FailedCommandNotificator(ErrorNotificator[CommandError]):
    """
    A context manager that notifies about failed commands (by default resulted with `CommandError` or its subclasses).

    When such an exception is raised within the scope of this context manager, the notification is triggered.

    Args:
        message: the message to be displayed in the notification. If `None`, the message from the exception is used.
        catch_only: the type of exception to be caught and notified about. If `None`, all exceptions deriving from
            CommandError are caught. When a specific exception type is set, only those exceptions are caught.
    """

    def __init__(self, message: str | None = None, *, catch_only: type[CommandError] | None = None) -> None:
        super().__init__()
        self._message = message
        self._catch_only = catch_only

    def _is_exception_to_catch(self, exception: Exception) -> TypeGuard[CommandError]:
        if self._catch_only:
            return type(exception) is self._catch_only
        return isinstance(exception, CommandError)

    def _determine_message(self, exception: CommandError) -> str:
        if self._message:
            return self._message
        return str(exception)
