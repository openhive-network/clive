from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from textual import work
from textual.reactive import var

from clive.__private.config import settings
from clive.__private.core.commands.data_retrieval.governance_data import GovernanceData
from clive.__private.ui.widgets.clive_widget import CliveWidget

if TYPE_CHECKING:
    from textual.worker import Worker


class GovernanceDataProvider(CliveWidget):
    """
    A class for retrieving information about governance stored in a GovernanceData dataclass.

    To access the data after initializing the class, use the 'content' property.
    Management of governance data refreshing should be handled by a context manager, but also can be by stop_refreshing_data
    method.
    """

    content: GovernanceData = var(GovernanceData(), init=False)  # type: ignore[assignment]
    """It is used to check whether governance data has been refreshed and to store governance data."""

    def __init__(self) -> None:
        super().__init__()
        self.update_governance_data()
        self.interval = self.set_interval(settings.get("node.refresh_rate", 1.5), self.update_governance_data)

        self.__witness_pattern: str = ""
        self.__limit: int = 150
        self.__mode: Literal["search_by_name", "search_top"] = "search_top"
        self.__witness_name_pattern: str | None = None

    @work(name="governance data update worker")
    async def update_governance_data(self) -> None:
        proxy = self.app.world.profile_data.working_account.data.proxy
        account_name = proxy if proxy else self.app.world.profile_data.working_account.name

        wrapper = await self.app.world.commands.retrieve_governance_data(
            account_name=account_name,
            limit=self.__limit,
            mode=self.__mode,
            witness_name_pattern=self.__witness_name_pattern,
        )

        if wrapper.error_occurred:
            self.notify(f"Failed to retrieve savings data: {wrapper.error}", severity="error")
            return

        result = wrapper.result_or_raise
        if result.number_of_votes != self.content.number_of_votes or result.witness_names != self.content.witness_names:
            if self.__mode == "search_by_name" and self.content.witnesses is not None and result.witnesses is not None:
                for witness in self.content.witnesses.items():
                    if witness[0] in result.witnesses:
                        result.witnesses[witness[0]].rank = witness[1].rank

            self.content = result

    def stop_refreshing_data(self) -> None:
        self.interval.stop()

    def set_mode_witnesses_by_name(self, pattern: str | None = None, limit: int = 150) -> Worker[None]:
        self.__mode = "search_by_name"
        self.__witness_name_pattern = pattern
        self.__limit = limit

        return self.update_governance_data()

    def set_mode_top_witnesses(self) -> Worker[None]:
        self.__mode = "search_top"
        self.__witness_name_pattern = None
        self.__limit = 150

        return self.update_governance_data()
