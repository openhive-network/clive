from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from textual import work
from textual.reactive import var

from clive.__private.config import settings
from clive.__private.ui.widgets.clive_widget import CliveWidget

if TYPE_CHECKING:
    from clive.models.aliased import SavingsWithdrawals


@dataclass
class SavingsData:
    pending_transfers: list[SavingsWithdrawals] | None = None
    hbd_interest_rate: int = 1000
    last_interest_payment: datetime = field(default_factory=lambda: datetime.utcfromtimestamp(0))


class SavingsDataProvider(CliveWidget):
    """
    A class for retrieving information about savings stored in a SavingsData dataclass.

    To access the data after initializing the class, use the content property.
    """

    content: SavingsData = var(SavingsData())  # type: ignore[assignment]
    """It is used to check whether savings data has been refreshed and to store savings data."""

    def __init__(self) -> None:
        super().__init__()
        self.interval = self.set_interval(settings.get("node.refresh_rate", 1.5), self._update_savings_data)  # type: ignore[arg-type]

    @work(name="savings data update worker")
    async def _update_savings_data(self) -> None:
        working_account_name = self.app.world.profile_data.working_account.name

        gdpo = await self.app.world.app_state.get_dynamic_global_properties()
        response_db_api = await self.app.world.node.api.database_api.find_accounts(accounts=[working_account_name])
        pending_transfers = await self.app.world.node.api.database_api.find_savings_withdrawals(
            account=working_account_name
        )

        new_savings_data = SavingsData(
            hbd_interest_rate=gdpo.hbd_interest_rate,
            last_interest_payment=response_db_api.accounts[0].savings_hbd_last_interest_payment,
            pending_transfers=pending_transfers.withdrawals,
        )

        if self.content != new_savings_data:
            self.content = new_savings_data
