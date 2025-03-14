from __future__ import annotations

from typing import TYPE_CHECKING

from textual.reactive import var

from clive.__private.core.commands.data_retrieval.proposals_data import ProposalsData, ProposalsDataRetrieval
from clive.__private.ui.data_providers.abc.data_provider import DataProvider

if TYPE_CHECKING:
    from textual.worker import Worker


class ProposalsDataProvider(DataProvider[ProposalsData]):
    _content: ProposalsData | None = var(None, init=False)  # type: ignore[assignment]

    def __init__(self, *, paused: bool = False, init_update: bool = True) -> None:
        super().__init__(paused=paused, init_update=init_update)
        self.__order: ProposalsDataRetrieval.Orders = ProposalsDataRetrieval.DEFAULT_ORDER
        self.__order_direction: ProposalsDataRetrieval.OrderDirections = ProposalsDataRetrieval.DEFAULT_ORDER_DIRECTION
        self.__status: ProposalsDataRetrieval.Statuses = ProposalsDataRetrieval.DEFAULT_STATUS

    async def _update(self) -> None:
        proxy = self.profile.accounts.working.data.proxy
        account_name = proxy if proxy else self.profile.accounts.working.name

        wrapper = await self.commands.retrieve_proposals_data(
            account_name=account_name, order=self.__order, order_direction=self.__order_direction, status=self.__status
        )

        if wrapper.error_occurred:
            self.notify("Failed to retrieve proposals data.", severity="error")
            return

        result = wrapper.result_or_raise

        if not self.is_content_set:
            self._content = result
            return

        if result.proposals != self.content.proposals:
            self._content = result

    def change_order(
        self,
        order: ProposalsDataRetrieval.Orders,
        order_direction: ProposalsDataRetrieval.OrderDirections,
        status: ProposalsDataRetrieval.Statuses,
    ) -> Worker[None]:
        self.__order = order
        self.__order_direction = order_direction
        self.__status = status

        return self.update()
