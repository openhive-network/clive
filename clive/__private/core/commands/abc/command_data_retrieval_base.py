from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from clive.__private.stopwatch import Stopwatch

HarvestedDataT = TypeVar("HarvestedDataT")
SanitizedDataT = TypeVar("SanitizedDataT")
ProcessedDataT = TypeVar("ProcessedDataT")


@dataclass(kw_only=True)
class CommandDataRetrievalBase(Generic[HarvestedDataT, SanitizedDataT, ProcessedDataT], ABC):
    """
    A Command for retrieving data from an external source via an API.

    This command is used to send requests to an API and possibly collect data as a result.
    """

    @abstractmethod
    async def _harvest_data_from_api(self) -> HarvestedDataT:
        """Gather data from an API and return it."""

    async def _sanitize_data(self, data: HarvestedDataT) -> SanitizedDataT:
        """Sanitize the data and return it."""
        return data  # type: ignore[return-value]

    async def _process_data(self, data: SanitizedDataT) -> ProcessedDataT:
        """Process the data and return the result."""
        return data  # type: ignore[return-value]

    async def _perform_data_operations(self) -> ProcessedDataT:
        name = self.__class__.__name__
        with Stopwatch(f"Harvesting: {name}"):
            harvested_data = await self._harvest_data_from_api()

        with Stopwatch(f"Sanitizing: {name}"):
            sanitized_data = await self._sanitize_data(harvested_data)

        with Stopwatch(f"Processing: {name}"):
            return await self._process_data(sanitized_data)
