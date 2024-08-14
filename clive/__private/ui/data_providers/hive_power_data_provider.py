from __future__ import annotations

from textual import work
from textual.reactive import var

from clive.__private.core.commands.data_retrieval.hive_power_data import HivePowerData
from clive.__private.ui.data_providers.abc.data_provider import DataProvider


class HivePowerDataProvider(DataProvider[HivePowerData]):
    _content: HivePowerData | None = var(None, init=False)  # type: ignore[assignment]

    def __init__(self, *, paused: bool = False, init_update: bool = True) -> None:
        super().__init__(paused=paused, init_update=init_update)

    @work(name="hive power data update worker")
    async def update(self) -> None:
        account_name = self.profile.accounts.working.name

        wrapper = await self.commands.retrieve_hp_data(account_name=account_name)

        if wrapper.error_occurred:
            self.notify(f"Failed to retrieve hive power data: {wrapper.error}", severity="error")
            return

        result = wrapper.result_or_raise
        self._content = result
