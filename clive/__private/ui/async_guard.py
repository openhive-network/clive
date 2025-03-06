from __future__ import annotations

import asyncio
import contextlib
from contextlib import contextmanager
from typing import TYPE_CHECKING

from clive.exceptions import CliveError

if TYPE_CHECKING:
    from typing import Generator


class AsyncGuardNotAvailableError(CliveError):
    """Raised when trying to engage a guard that is already engaged."""


class AsyncGuard:
    def __init__(self) -> None:
        self._event = asyncio.Event()

    def is_available(self) -> bool:
        """
        Check if the event lock is currently available (not engaged).

        Use this to determine if an instruction can proceed with no conflicts.
        """
        return not self._event.is_set()

    @contextmanager
    def guard(self) -> Generator[None, None, None]:
        """
        Prevents concurrent execution of the block by raising an appropriate error.

        Can be used together with `suppress`. Look into its documentation for more details.

        Usage:
            async with event_guard.guard():
                # Protected code which shouldn't be executed concurrently
        """
        if not self.is_available():
            raise AsyncGuardNotAvailableError("Guard is already engaged")
        self._event.set()
        try:
            yield
        finally:
            self._event.clear()

    @staticmethod
    @contextmanager
    def suppress() -> Generator[None, None, None]:
        """
        Suppresses the AsyncGuardNotAvailableError error raised by the guard.

        Use this together with `guard` to skip code execution when like below.

        Usage:
            with event_guard.suppress(), event_guard.guard():
                # Code that should be skipped when guard is engaged
        """
        with contextlib.suppress(AsyncGuardNotAvailableError):
            yield
