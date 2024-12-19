from __future__ import annotations

import asyncio
import contextlib
from collections.abc import Generator
from typing import Final

from clive.__private.logger import logger
from clive.exceptions import CliveError


class AsyncGuardNotAvailableError(CliveError):
    """Raised when trying to acquire a guard that is already acquired."""

    MESSAGE: Final[str] = "Guard is already acquired."

    def __init__(self) -> None:
        super().__init__(self.MESSAGE)


class AsyncGuard:
    """
    A helper class to manage an asynchronous event-like lock, ensuring exclusive execution.

    Use this for scenarios where you want to prevent concurrent execution of an async task.
    When the guard is acquired by some other task, the guarded block could not execute, error will be raised instead.
    Can be used together with `suppress`. Look into its documentation for more details.
    """

    def __init__(self) -> None:
        self._event = asyncio.Event()

    @property
    def is_available(self) -> bool:
        """Return True if the event lock is currently available (not acquired)."""
        return not self._event.is_set()

    def acquire(self) -> None:
        if not self.is_available:
            raise AsyncGuardNotAvailableError

        self._event.set()

    def release(self) -> None:
        self._event.clear()

    @contextlib.contextmanager
    def guard(self) -> Generator[None]:
        self.acquire()
        try:
            yield
        finally:
            self.release()

    @staticmethod
    @contextlib.contextmanager
    def suppress() -> Generator[None]:
        """
        Suppresses the AsyncGuardNotAvailable error raised by the guard.

        Use this together with `acquire` or `guard` to skip code execution when the guard is acquired.
        """
        try:
            yield
        except AsyncGuardNotAvailableError:
            logger.debug("Suppressing AsyncGuardNotAvailableError.")
