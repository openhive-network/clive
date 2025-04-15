from __future__ import annotations

from abc import abstractmethod
from typing import Final

from inflection import underscore
from textual import on
from textual.containers import Container
from textual.reactive import var
from textual.worker import Worker, WorkerState

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.settings import safe_settings
from clive.__private.ui.clive_screen import CliveScreen
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.not_updated_yet import NotUpdatedYet, is_not_updated_yet
from clive.exceptions import CliveError


class ProviderError(CliveError):
    """Base exception for all provider-related exceptions."""


class ProviderNotSetYetError(ProviderError):
    _MESSAGE: Final[str] = """
Provider content was referenced before the update actually occurred.
You're probably using it too early.
If you are sure, you can use the `updated` property to check if content is ready
 or `_content` which may be NotUpdatedYet."""

    def __init__(self) -> None:
        super().__init__(self._MESSAGE)


class DataProvider[ProviderContentT](Container, CliveWidget, AbstractClassMessagePump):
    """
    Retrieve data in a periodic manner. Data is stored in the reactive attributes.

    To access the data, use the content reactive attribute.
    Management of data refreshing/cleanup could be done by using DataProvider as a context manager in compose() like
    method, but could be also done by using the provider methods.
    """

    _content: ProviderContentT | NotUpdatedYet = var(NotUpdatedYet(), init=False)  # type: ignore[assignment]
    """Should be overridden by subclasses to store the data retrieved by the provider."""

    updated: bool = var(default=False)  # type: ignore[assignment]
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

        self.interval = self.set_interval(
            safe_settings.node.refresh_rate_secs, self._update_if_not_ongoing, pause=paused
        )

    def update(self) -> Worker[None]:
        name = self.get_worker_name()
        return self.run_worker(self._update(), name=name, group=name, exclusive=True)

    @abstractmethod
    async def _update(self) -> None:
        """
        Define the logic to update the provider data.

        The name and group of the worker is inferred from the class name.
        """

    @on(Worker.StateChanged)
    def set_updated(self, event: Worker.StateChanged) -> None:
        if event.state == WorkerState.SUCCESS:
            self.updated = True

    @property
    def content(self) -> ProviderContentT:
        if not self.is_content_set:
            raise ProviderNotSetYetError
        assert not isinstance(self._content, NotUpdatedYet), "Already checked."
        return self._content

    @property
    def is_content_set(self) -> bool:
        return not is_not_updated_yet(self._content)

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

    def get_worker_name(self) -> str:
        return f"{underscore(self.__class__.__name__)} update worker"

    def _update_if_not_ongoing(self) -> None:
        name = self.get_worker_name()
        if self.app.is_worker_group_empty(name):
            self.update()
