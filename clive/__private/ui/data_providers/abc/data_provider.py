from __future__ import annotations

from abc import abstractmethod

from textual import work

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.config import settings
from clive.__private.ui.widgets.clive_widget import CliveWidget


class BaseDataProvider(CliveWidget, AbstractClassMessagePump):
    def __init__(self) -> None:
        super().__init__()
        self.update_provider_data()
        self.interval = self.set_interval(settings.get("node.refresh_rate", 1.5), self.update_provider_data)

    @abstractmethod
    @work
    async def update_provider_data(self) -> None:
        """The name of the worker can be included by overriding the work decorator, for example: @work("my work")."""

    def stop_refreshing_data(self) -> None:
        self.interval.stop()
