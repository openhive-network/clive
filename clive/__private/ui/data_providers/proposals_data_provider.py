from __future__ import annotations

from typing import TYPE_CHECKING

from textual import work
from textual.reactive import var

from clive.__private.core.commands.data_retrieval.proposals_data import ProposalsData, ProposalsDataRetrieval
from clive.__private.ui.data_providers.abc.data_provider import DataProvider

if TYPE_CHECKING:
    from textual.worker import Worker


class ProposalsDataProvider(DataProvider):
    content: ProposalsData = var(ProposalsData(), init=False)  # type: ignore[assignment]

    def __init__(self) -> None:
        super().__init__()
        self.__mode = ProposalsDataRetrieval.DEFAULT_MODE
        self.__order_direction = ProposalsDataRetrieval.DEFAULT_ORDER_DIRECTION
        self.__status = ProposalsDataRetrieval.DEFAULT_STATUS

    @work(name="proposals data update worker")
    async def update(self) -> None:
        proxy = self.app.world.profile_data.working_account.data.proxy
        account_name = proxy if proxy else self.app.world.profile_data.working_account.name

        wrapper = await self.app.world.commands.retrieve_proposals_data(
            account_name=account_name, mode=self.__mode, order_direction=self.__order_direction, status=self.__status
        )

        if wrapper.error_occurred:
            self.notify(f"Failed to retrieve proposals data: {wrapper.error}", severity="error")
            return

        result = wrapper.result_or_raise
        if result.proposals != self.content.proposals:
            self.content = result

    def change_order(self, mode: str, order_direction: str, status: str) -> Worker[None]:
        self.__mode = mode
        self.__order_direction = order_direction
        self.__status = status

        return self.update()
