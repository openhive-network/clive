from __future__ import annotations

from textual.reactive import var

from clive.__private.core.commands.data_retrieval.hive_power_data import HivePowerData
from clive.__private.ui.data_providers.abc.data_provider import DataProvider


class HivePowerDataProvider(DataProvider[HivePowerData]):
    _content: HivePowerData | None = var(None, init=False)  # type: ignore[assignment]

    def __init__(self, *, paused: bool = False, init_update: bool = True) -> None:
        super().__init__(paused=paused, init_update=init_update)

    async def _update(self) -> None:
        account_name = self.profile.accounts.working.name

        wrapper = await self.commands.retrieve_hp_data(account_name=account_name)

        if wrapper.error_occurred:
            self.notify("Failed to retrieve hive power data.", severity="error")
            return

        result = wrapper.result_or_raise
        self._content = result
