from __future__ import annotations

from textual.reactive import var

from clive.__private.core.commands.data_retrieval.savings_data import SavingsData
from clive.__private.ui.data_providers.abc.data_provider import DataProvider
from clive.__private.ui.not_updated_yet import NotUpdatedYet


class SavingsDataProvider(DataProvider[SavingsData]):
    """A class for retrieving information about savings stored in a SavingsData dataclass."""

    _content: SavingsData | NotUpdatedYet = var(NotUpdatedYet(), init=False)  # type: ignore[assignment]
    """It is used to check whether savings data has been refreshed and to store savings data."""

    async def _update(self) -> None:
        account_name = self.profile.accounts.working.name
        wrapper = await self.commands.retrieve_savings_data(account_name=account_name)

        if wrapper.error_occurred:
            self.notify("Failed to retrieve savings data.", severity="error")
            return

        result = wrapper.result_or_raise
        self._content = result
