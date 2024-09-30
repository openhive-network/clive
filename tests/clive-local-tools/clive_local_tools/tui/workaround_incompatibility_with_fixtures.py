"""
Workaround for Textual incompatibility with pytest fixtures due to context isolation in pytest-asyncio.

See:
- https://github.com/Textualize/textual/issues/4998
- https://github.com/pytest-dev/pytest-asyncio/issues/127
"""

from __future__ import annotations

import asyncio
import contextvars
import functools
import traceback
from pathlib import Path
from typing import Any, Coroutine, Generator

import pytest

Task310 = asyncio.tasks._PyTask  # type: ignore[attr-defined]


class Task311(Task310):  # type: ignore[misc, valid-type]
    """
    Backport of Task from CPython 3.11.

    It's needed to allow context passing
    """

    def __init__(
        self,
        coro: Coroutine[Any, Any, Any],
        *,
        loop: asyncio.AbstractEventLoop | None = None,
        name: str | None = None,
        context: contextvars.Context | None = None,
    ) -> None:
        super(Task310, self).__init__(loop=loop)
        if self._source_traceback:
            del self._source_traceback[-1]
        if not asyncio.coroutines.iscoroutine(coro):
            # raise after Future.__init__(), attrs are required for __del__
            # prevent logging for pending task in __del__
            self._log_destroy_pending = False
            raise TypeError(f"a coroutine was expected, got {coro!r}")

        if name is None:
            self._name = f"Task-{asyncio.tasks._task_name_counter()}"  # type: ignore[attr-defined]
        else:
            self._name = str(name)

        self._num_cancels_requested = 0
        self._must_cancel = False
        self._fut_waiter = None
        self._coro = coro
        if context is None:
            self._context = contextvars.copy_context()
        else:
            self._context = context

        self._loop.call_soon(self._Task__step, context=self._context)
        asyncio.tasks._register_task(self)


def task_factory(
    loop: asyncio.AbstractEventLoop, coro: Coroutine[Any, Any, Any], context: contextvars.Context | None = None
) -> Task311:
    stack = traceback.extract_stack()
    for frame in stack[-2::-1]:
        package_name = Path(frame.filename).parts[-2]
        if package_name != "asyncio":
            if package_name == "pytest_asyncio":
                # This function was called from pytest_asyncio, use shared context
                break
            # This function was called from somewhere else, create context copy
            context = None
            break
    return Task311(coro, loop=loop, context=context)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop]:
    """
    Workaround for context isolation in pytest-asyncio.

    This fixture is used by pytest-asyncio to run test's setup/run/teardown.
    It's needed to share contextvars between these stages.
    This breaks context isolation for tasks, so we need to check calling context there.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    context = contextvars.copy_context()
    loop.set_task_factory(functools.partial(task_factory, context=context))
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()
