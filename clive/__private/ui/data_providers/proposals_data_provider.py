from __future__ import annotations

from typing import TYPE_CHECKING

from textual import work
from textual.reactive import var

from clive.__private.core.commands.data_retrieval.proposals_data import ProposalsData, ProposalsDataRetrieval
from clive.__private.ui.data_providers.abc.data_provider import DataProvider

if TYPE_CHECKING:
    from textual.worker import Worker


class ProposalsDataProvider(DataProvider[ProposalsData]):
    _content: ProposalsData | None = var(None, init=False)  # type: ignore[assignment]

    def __init__(self, *, paused: bool = False, init_update: bool = True) -> None:
        super().__init__(paused=paused, init_update=init_update)
        self.__order = ProposalsDataRetrieval.DEFAULT_ORDER
        self.__order_direction = ProposalsDataRetrieval.DEFAULT_ORDER_DIRECTION
        self.__status = ProposalsDataRetrieval.DEFAULT_STATUS

    @work(name="proposals data update worker")
    async def update(self) -> None:
        proxy = self.app.world.profile_data.working_account.data.proxy
        account_name = proxy if proxy else self.app.world.profile_data.working_account.name

        wrapper = await self.app.world.commands.retrieve_proposals_data(
            account_name=account_name, order=self.__order, order_direction=self.__order_direction, status=self.__status
        )

        if wrapper.error_occurred:
            self.notify(f"Failed to retrieve proposals data: {wrapper.error}", severity="error")
            return

        result = wrapper.result_or_raise

        if not self.updated:
            self._content = result
            return

        if result.proposals != self.content.proposals:
            self._content = result

    def change_order(self, order: str, order_direction: str, status: str) -> Worker[None]:
        self.__order = order
        self.__order_direction = order_direction
        self.__status = status

        return self.update()
