from __future__ import annotations

from abc import abstractmethod

from textual import on, work
from textual.reactive import var
from textual.worker import Worker, WorkerState

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.config import settings
from clive.__private.ui.widgets.clive_widget import CliveWidget


class DataProvider(CliveWidget, AbstractClassMessagePump):
    """
    Retrieve data in a periodic manner. Data is stored in the reactive attributes.

    To access the data, use the content reactive attribute.
    Management of data refreshing/cleanup could be done by using DataProvider as a context manager in compose() like
    method, but could be also done by using the provider methods.
    """

    content: object = var(None, init=False)
    """Should be overridden by subclasses to store the data retrieved by the provider."""

    updated: bool = var(False)  # type: ignore[assignment]
    """Set to True when the provider has updated the content for the first time."""

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

    def stop(self) -> None:
        self.interval.stop()

    def pause(self) -> None:
        self.interval.pause()

    def resume(self) -> None:
        self.interval.resume()

    def restart(self) -> Worker[None]:
        worker = self.update()
        self.interval.reset()
        self.interval.resume()

        return worker
