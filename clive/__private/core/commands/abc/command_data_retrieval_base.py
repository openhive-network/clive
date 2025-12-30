from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from clive.__private.stopwatch import Stopwatch

HarvestedDataT = TypeVar("HarvestedDataT")
SanitizedDataT = TypeVar("SanitizedDataT")
ProcessedDataT = TypeVar("ProcessedDataT")


@dataclass(kw_only=True, replace=False)  # type: ignore[call-overload]
class CommandDataRetrievalBase(ABC, Generic[HarvestedDataT, SanitizedDataT, ProcessedDataT]):  # noqa: UP046
    """
    A Command for retrieving data from an external source via an API.

    This command is used to send requests to an API and possibly collect data as a result.
    """

    @abstractmethod
    async def _harvest_data_from_api(self) -> HarvestedDataT:
        """
        Harvest raw data from an external API source.

        Subclasses must implement this to fetch data from specific APIs.
        All calls to the API should be made only within this method.

        Returns:
            The raw data retrieved from the API.
        """

    async def _sanitize_data(self, data: HarvestedDataT) -> SanitizedDataT:
        """
        Sanitize the harvested data to prepare it for processing.

        This method cleans, validates, and transforms the raw data from the API into a format
        that can be safely processed. By default, it returns the input data unchanged, but
        subclasses can override this to implement custom sanitization logic.

        Args:
            data: The raw data harvested from the API.

        Returns:
            The sanitized data.
        """
        return data  # type: ignore[return-value]

    async def _process_data(self, data: SanitizedDataT) -> ProcessedDataT:
        """
        Process the sanitized data into the final output format.

        This method transforms the sanitized data into the desired output format. By default,
        it returns the sanitized data unchanged, but subclasses can override this to implement
        custom processing logic such as filtering, aggregating, or transforming the data.

        Args:
            data: The sanitized data to process.

        Returns:
            The processed data.
        """
        return data  # type: ignore[return-value]

    async def _perform_data_operations(self) -> ProcessedDataT:
        name = self.__class__.__name__
        with Stopwatch(f"Harvesting: {name}"):
            harvested_data = await self._harvest_data_from_api()

        with Stopwatch(f"Sanitizing: {name}"):
            sanitized_data = await self._sanitize_data(harvested_data)

        with Stopwatch(f"Processing: {name}"):
            return await self._process_data(sanitized_data)
