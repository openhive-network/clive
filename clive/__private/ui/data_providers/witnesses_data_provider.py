from __future__ import annotations

from typing import TYPE_CHECKING

from textual.reactive import var

from clive.__private.core.commands.data_retrieval.witnesses_data import WitnessesData, WitnessesDataRetrieval
from clive.__private.ui.data_providers.abc.data_provider import DataProvider
from clive.__private.ui.not_updated_yet import NotUpdatedYet

if TYPE_CHECKING:
    from textual.worker import Worker


class WitnessesDataProvider(DataProvider[WitnessesData]):
    """
    A class for retrieving information about witnesses.

    Args:
        paused: Whether the data provider is paused.
        init_update: Whether to perform an initial update.
    """

    _content: WitnessesData | NotUpdatedYet = var(NotUpdatedYet(), init=False)  # type: ignore[assignment]
    """It is used to check whether witnesses data has been refreshed and to store witnesses data."""

    def __init__(self, *, paused: bool = False, init_update: bool = True) -> None:
        super().__init__(paused=paused, init_update=init_update)

        self.__witness_pattern: str = ""
        self.__search_by_pattern_limit: int = WitnessesDataRetrieval.DEFAULT_SEARCH_BY_PATTERN_LIMIT
        self.__mode: WitnessesDataRetrieval.Modes = WitnessesDataRetrieval.DEFAULT_MODE
        self.__witness_name_pattern: str | None = None

    async def _update(self) -> None:
        proxy = self.profile.accounts.working.data.proxy
        account_name = proxy if proxy else self.profile.accounts.working.name

        wrapper = await self.commands.retrieve_witnesses_data(
            account_name=account_name,
            mode=self.__mode,
            witness_name_pattern=self.__witness_name_pattern,
            search_by_pattern_limit=self.__search_by_pattern_limit,
        )

        if wrapper.error_occurred:
            self.notify("Failed to retrieve witnesses data.", severity="error")
            return

        result = wrapper.result_or_raise

        if not self.is_content_set:
            self._content = result
            return

        if result.number_of_votes != self.content.number_of_votes or result.witness_names != self.content.witness_names:
            self._content = result

    def set_mode_witnesses_by_name(
        self, pattern: str | None = None, limit: int = WitnessesDataRetrieval.DEFAULT_SEARCH_BY_PATTERN_LIMIT
    ) -> Worker[None]:
        self.__mode = "search_by_pattern"
        self.__witness_name_pattern = pattern
        self.__search_by_pattern_limit = limit

        return self.update()

    def set_mode_top_witnesses(self) -> Worker[None]:
        self.__mode = WitnessesDataRetrieval.DEFAULT_MODE
        self.__witness_name_pattern = None
        self.__search_by_pattern_limit = WitnessesDataRetrieval.DEFAULT_SEARCH_BY_PATTERN_LIMIT

        return self.update()
