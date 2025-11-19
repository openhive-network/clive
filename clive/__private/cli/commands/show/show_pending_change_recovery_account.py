from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Final

from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.print_cli import print_cli, print_content_not_available
from clive.__private.core.accounts.accounts import TrackedAccount
from clive.__private.core.formatters.humanize import (
    humanize_datetime,
    humanize_timedelta,
)

if TYPE_CHECKING:
    from clive.__private.core.alarms.specific_alarms.changing_recover_account_in_progress import (
        ChangingRecoveryAccountInProgress,
        ChangingRecoveryAccountInProgressAlarmData,
    )


NO_PENDING_ACCOUNT_RECOVERY_MESSAGE: Final[str] = "No pending change recovery account request."


@dataclass(kw_only=True)
class ShowPendingChangeRecoveryAccount(WorldBasedCommand):
    account_name: str
    _alarm: ChangingRecoveryAccountInProgress = field(init=False)

    async def fetch_data(self) -> None:
        account = TrackedAccount(name=self.account_name)
        await self.world.commands.update_node_data(accounts=[account])
        await self.world.commands.update_alarms_data(accounts=[account])

        alarm = account.alarms.changing_recovery_account_in_progress
        self._alarm = alarm

    async def _run(self) -> None:
        if self._alarm.is_active:
            change_recovery_account_info_table = self._create_pending_change_recovery_account_info_table(
                self._alarm.alarm_data_ensure
            )
            print_cli(change_recovery_account_info_table)
            return
        print_content_not_available(NO_PENDING_ACCOUNT_RECOVERY_MESSAGE)

    def _create_pending_change_recovery_account_info_table(
        self, data: ChangingRecoveryAccountInProgressAlarmData
    ) -> Table:
        table = Table(title=self._format_table_title(self.account_name), show_header=False)
        table.add_row("Start data", humanize_datetime(data.start_date))
        table.add_row("End date", humanize_datetime(data.end_date))
        table.add_row("Time left", humanize_timedelta(data.time_left))
        table.add_row("New recovery account", data.new_recovery_account)
        return table

    @classmethod
    def _format_table_title(cls, account_name: str) -> str:
        return f"Request to change recovery account for account `{account_name}`"
