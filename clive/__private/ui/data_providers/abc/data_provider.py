from __future__ import annotations

from abc import abstractmethod
from typing import Final, Generic, TypeVar

from textual import on, work
from textual.containers import Container
from textual.reactive import var
from textual.worker import Worker, WorkerState

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.config import settings
from clive.__private.ui.widgets.clive_screen import CliveScreen
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.exceptions import CliveError

ProviderContentT = TypeVar("ProviderContentT")


class ProviderError(CliveError):
    """Base exception for all provider-related exceptions."""


class ProviderNotSetYetError(ProviderError):
    _MESSAGE: Final[str] = """
Provider content was referenced before the update actually occurred.
You're probably using it too early.
If you are sure, you can use the `updated` property to check if content is ready or `_content` which may be None."""

    def __init__(self) -> None:
        super().__init__(self._MESSAGE)


class DataProvider(Container, CliveWidget, Generic[ProviderContentT], AbstractClassMessagePump):
    """
    Retrieve data in a periodic manner. Data is stored in the reactive attributes.

    To access the data, use the content reactive attribute.
    Management of data refreshing/cleanup could be done by using DataProvider as a context manager in compose() like
    method, but could be also done by using the provider methods.
    """

    _content: ProviderContentT | None = var(None, init=False)  # type: ignore[assignment]
    """Should be overridden by subclasses to store the data retrieved by the provider."""

    updated: bool = var(False)  # type: ignore[assignment]
    """
    Set to True when the provider has updated the content for the first time. Can be watched.

    Warning: In case when you have to check if the content is ready in the watch callback method,
    use `is_content_set` instead, as `updated` may be set to True **after** notifying watchers.
    Flow looks like this:
    1. Provider is created.
    2. Provider is updated for the first time.
    3. `is_content_set` will return True.
    4. Watchers are notified.
    3. `updated` is set to True.
    """

    def __init__(self, *, paused: bool = False, init_update: bool = True) -> None:
        super().__init__()

        if not paused and init_update:
            self.update()

        self.interval = self.set_interval(settings.get("node.refresh_rate", 1.5), self.update, pause=paused)

    @abstractmethod
    @work
    async def update(self) -> None:
        """
        Define the logic to update the provider data.

        The name of the worker can be included by overriding the work decorator, e.g.: @work("my work").
        """

    @on(Worker.StateChanged)
    def set_updated(self, event: Worker.StateChanged) -> None:
        if event.state == WorkerState.SUCCESS:
            self.updated = True

    @property
    def content(self) -> ProviderContentT:
        if self._content is None:
            raise ProviderNotSetYetError
        return self._content

    @property
    def is_content_set(self) -> bool:
        return self._content is not None

    def stop(self) -> None:
        self.interval.stop()

    @on(CliveScreen.Suspended)
    def pause(self) -> None:
        self.interval.pause()

    @on(CliveScreen.Resumed)
    def resume(self) -> None:
        self.interval.resume()

    def restart(self) -> Worker[None]:
        worker = self.update()
        self.interval.reset()
        self.interval.resume()

        return worker
