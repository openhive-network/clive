from __future__ import annotations

from typing import TYPE_CHECKING, Final

from clive.__private.core.clive_import import get_clive
from clive.__private.core.commands.abc.command_safe import CommandSafeExecutionError
from clive.__private.logger import logger
from clive.__private.ui.widgets.notification import Notification

if TYPE_CHECKING:
    from types import TracebackType

    from typing_extensions import Self


class FailedCommandNotificator:
    """
    A context manager that notifies about failed commands (Resulted with `CommandSafeExecutionError`).
    When such an exception is raised within the scope of this context manager, the notification is triggered.
    """

    DEFAULT_MESSAGE: Final[str] = "Action failed. Please try again..."

    def __init__(self, message: str = DEFAULT_MESSAGE) -> None:
        self.__message = message

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> bool:
        if exc_type and exc_type is CommandSafeExecutionError:
            self.__notify()
            return True
        return False

    def __notify(self) -> None:
        if get_clive().is_launched:
            self.__notify_tui()
            return

        logger.warning("Command failed and no one was notified.")

    def __notify_tui(self) -> None:
        Notification(self.__message, category="error").show()
