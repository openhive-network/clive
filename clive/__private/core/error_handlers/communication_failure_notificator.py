from __future__ import annotations

from typing import TYPE_CHECKING, Final

from clive.__private.core.clive_import import get_clive
from clive.__private.logger import logger
from clive.__private.ui.widgets.notification import Notification
from clive.exceptions import CommunicationError

if TYPE_CHECKING:
    from collections.abc import Callable
    from types import TracebackType

    from typing_extensions import Self


class CommunicationFailureNotificator:
    """A context manager that notifies about errors of `CommunicatorError` type."""

    SEARCHED_AND_PRINTED_MESSAGES: Final[dict[str, str]] = {
        "does not have sufficient funds": "You don't have enough funds to perform this operation.",
    }

    def __init__(self) -> None:
        self.error_occurred = False

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> bool:
        self.error_occurred = exc_type is not None

        if self.error_occurred and isinstance(exc_val, CommunicationError):
            self.__notify(exc_val)
            return True
        return False

    def execute(self, func: Callable[..., None]) -> None:
        try:
            func()
        except CommunicationError as error:
            self.error_occurred = True
            self.__notify(error)
        except Exception:
            self.error_occurred = True
            raise

    def __notify(self, exception: CommunicationError) -> None:
        message = self.__determine_message(exception)

        if get_clive().is_launched:
            self.__notify_tui(message)
            return

        logger.warning(f"Command failed and no one was notified. {message=}")

    @classmethod
    def __determine_message(cls, exception: CommunicationError) -> str:
        exception_raw = str(exception)

        for searched, printed in cls.SEARCHED_AND_PRINTED_MESSAGES.items():
            if searched in exception_raw:
                return printed
        return exception_raw

    @staticmethod
    def __notify_tui(message: str) -> None:
        Notification(message, category="error").show()
