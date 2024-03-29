from __future__ import annotations

from typing import TYPE_CHECKING

from textual import work
from textual.reactive import var

from clive.__private.core.commands.data_retrieval.witnesses_data import WitnessesData, WitnessesDataRetrieval
from clive.__private.ui.data_providers.abc.data_provider import DataProvider

if TYPE_CHECKING:
    from textual.worker import Worker


class WitnessesDataProvider(DataProvider[WitnessesData]):
    """A class for retrieving information about witnesses stored in a WitnessesData dataclass."""

    _content: WitnessesData | None = var(None, init=False)  # type: ignore[assignment]
    """It is used to check whether witnesses data has been refreshed and to store witnesses data."""

    def __init__(self, *, paused: bool = False, init_update: bool = True) -> None:
        super().__init__(paused=paused, init_update=init_update)

        self.__witness_pattern: str = ""
        self.__search_by_name_limit: int = WitnessesDataRetrieval.DEFAULT_SEARCH_BY_NAME_LIMIT
        self.__mode: WitnessesDataRetrieval.Modes = WitnessesDataRetrieval.DEFAULT_MODE
        self.__witness_name_pattern: str | None = None

    @work(name="witnesses data update worker")
    async def update(self) -> None:
        proxy = self.app.world.profile_data.working_account.data.proxy
        account_name = proxy if proxy else self.app.world.profile_data.working_account.name

        wrapper = await self.app.world.commands.retrieve_witnesses_data(
            account_name=account_name,
            mode=self.__mode,
            witness_name_pattern=self.__witness_name_pattern,
            search_by_name_limit=self.__search_by_name_limit,
        )

        if wrapper.error_occurred:
            self.notify(f"Failed to retrieve witnesses data: {wrapper.error}", severity="error")
            return

        result = wrapper.result_or_raise

        if not self.is_content_set:
            self._content = result
            return

        if result.number_of_votes != self.content.number_of_votes or result.witness_names != self.content.witness_names:
            self._content = result

    def set_mode_witnesses_by_name(
        self, pattern: str | None = None, limit: int = WitnessesDataRetrieval.DEFAULT_SEARCH_BY_NAME_LIMIT
    ) -> Worker[None]:
        self.__mode = "search_by_pattern"
        self.__witness_name_pattern = pattern
        self.__search_by_name_limit = limit

        return self.update()

    def set_mode_top_witnesses(self) -> Worker[None]:
        self.__mode = WitnessesDataRetrieval.DEFAULT_MODE
        self.__witness_name_pattern = None
        self.__search_by_name_limit = WitnessesDataRetrieval.DEFAULT_SEARCH_BY_NAME_LIMIT

        return self.update()
