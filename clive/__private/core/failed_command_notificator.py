from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.clive_import import get_clive
from clive.__private.core.commands.abc.command import CommandError
from clive.__private.logger import logger
from clive.__private.ui.widgets.notification import Notification

if TYPE_CHECKING:
    from types import TracebackType

    from typing_extensions import Self


class FailedCommandNotificator:
    """
    A context manager that notifies about failed commands (by default resulted with `CommandError` or its subclasses).
    When such an exception is raised within the scope of this context manager, the notification is triggered.

    Params:
        message: the message to be displayed in the notification. If `None`, the message from the exception is used.
        catch_only: the type of exception to be caught and notified about. If `None`, all exceptions deriving from
            CommandError are caught. When a specific exception type is set, only those exceptions are caught.
    """

    def __init__(self, message: str | None = None, *, catch_only: type[CommandError] | None = None) -> None:
        self.__message = message
        self.__catch_only = catch_only

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> bool:
        if exc_val and self.__is_exception_to_catch(exc_val):
            self.__notify(exc_val)
            return True
        return False

    def __is_exception_to_catch(self, exception: BaseException) -> bool:
        if self.__catch_only:
            return type(exception) is self.__catch_only
        return isinstance(exception, CommandError)

    def __notify(self, exception: BaseException) -> None:
        message = self.__determine_message(exception)

        if get_clive().is_launched:
            self.__notify_tui(message)
            return

        logger.warning(f"Command failed and no one was notified. {message=}")

    def __determine_message(self, exception: BaseException) -> str:
        if self.__message:
            return self.__message
        return str(exception)

    @staticmethod
    def __notify_tui(message: str) -> None:
        Notification(message, category="error").show()
