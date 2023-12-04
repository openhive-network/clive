from __future__ import annotations

from textual import work
from textual.reactive import var

from clive.__private.core.commands.data_retrieval.savings_data import SavingsData
from clive.__private.ui.data_providers.abc.data_provider import BaseDataProvider


class SavingsDataProvider(BaseDataProvider):
    """
    A class for retrieving information about savings stored in a SavingsData dataclass.

    To access the data after initializing the class, use the 'content' property.
    Management of savings data refreshing should be handled by a context manager,
    but it can also be manually stopped using the 'stop' method.
    """

    content: SavingsData = var(SavingsData(), init=False)  # type: ignore[assignment]
    """It is used to check whether savings data has been refreshed and to store savings data."""

    @work(name="savings data update worker")
    async def update_provider_data(self) -> None:
        account_name = self.app.world.profile_data.working_account.name
        wrapper = await self.app.world.commands.retrieve_savings_data(account_name=account_name)

        if wrapper.error_occurred:
            self.notify(f"Failed to retrieve savings data: {wrapper.error}", severity="error")
            return

        result = wrapper.result_or_raise
        if self.content != result:
            self.content = result
