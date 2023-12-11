from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from textual import work
from textual.reactive import var

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.config import settings
from clive.__private.ui.widgets.clive_widget import CliveWidget

if TYPE_CHECKING:
    from textual.worker import Worker


class DataProvider(CliveWidget, AbstractClassMessagePump):
    """
    Retrieve data in a periodic manner. Data is stored in the reactive attributes.

    To access the data, use the content reactive attribute.
    Management of data refreshing/cleanup could be done by using DataProvider as a context manager in compose() like
    method, but could be also done by using the provider methods.
    """

    content: object = var(None, init=False)
    """Should be overridden by subclasses to store the data retrieved by the provider."""

    def __init__(self, paused: bool = True) -> None:
        super().__init__()
        self.interval = self.set_interval(settings.get("node.refresh_rate", 1.5), self.update, pause=paused)

    @abstractmethod
    @work
    async def update(self) -> None:
        """
        Define the logic to update the provider data.

        The name of the worker can be included by overriding the work decorator, e.g.: @work("my work").
        """

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
