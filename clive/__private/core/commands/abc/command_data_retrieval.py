from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from clive.__private.core.commands.abc.command_with_result import CommandResultT, CommandWithResult
from clive.__private.stopwatch import Stopwatch

HarvestedDataT = TypeVar("HarvestedDataT")
SanitizedDataT = TypeVar("SanitizedDataT")


@dataclass(kw_only=True)
class CommandDataRetrieval(
    CommandWithResult[CommandResultT], Generic[HarvestedDataT, SanitizedDataT, CommandResultT], ABC
):
    """
    A Command for retrieving data from an external source via an API.

    This command is used to send requests to an API and collect data as a result.
    It extends the CommandWithResult class to provide a result after execution.
    """

    @abstractmethod
    async def _harvest_data_from_api(self) -> HarvestedDataT:
        """Should gather data from an API and return it."""

    async def _sanitize_data(self, data: HarvestedDataT) -> SanitizedDataT:
        """Should sanitize the data and return it."""
        return data  # type: ignore[return-value]

    @abstractmethod
    async def _process_data(self, data: SanitizedDataT) -> CommandResultT:
        """Should process the data and return the result."""

    async def _execute(self) -> None:
        name = self.__class__.__name__
        with Stopwatch(f"Harvesting: {name}"):
            harvested_data = await self._harvest_data_from_api()

        with Stopwatch(f"Sanitizing: {name}"):
            sanitized_data = await self._sanitize_data(harvested_data)

        with Stopwatch(f"Processing: {name}"):
            result = await self._process_data(sanitized_data)
        self._result = result
