from __future__ import annotations

from clive.__private.core.commands.abc.command import CommandError
from clive.__private.core.error_handlers.abc.error_notificator import ErrorNotificator


class FailedCommandNotificator(ErrorNotificator):
    """
    A context manager that notifies about failed commands (by default resulted with `CommandError` or its subclasses).

    When such an exception is raised within the scope of this context manager, the notification is triggered.

    Args:
    ----
    message: the message to be displayed in the notification. If `None`, the message from the exception is used.
    catch_only: the type of exception to be caught and notified about. If `None`, all exceptions deriving from
        CommandError are caught. When a specific exception type is set, only those exceptions are caught.
    """

    def __init__(self, message: str | None = None, *, catch_only: type[CommandError] | None = None) -> None:
        super().__init__()
        self.__message = message
        self.__catch_only = catch_only

    def _is_exception_to_catch(self, exception: BaseException) -> bool:
        if self.__catch_only:
            return type(exception) is self.__catch_only
        return isinstance(exception, CommandError)

    def _determine_message(self, exception: BaseException) -> str:
        assert isinstance(exception, CommandError)

        if self.__message:
            return self.__message
        return str(exception)
