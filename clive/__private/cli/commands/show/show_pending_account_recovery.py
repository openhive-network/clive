from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Final

from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.print_cli import print_cli, print_content_not_available
from clive.__private.core.formatters.humanize import humanize_datetime

if TYPE_CHECKING:
    from schemas.apis.database_api import FindAccountRecoveryRequests
    from schemas.apis.database_api.fundaments_of_reponses import FindAccountRecoveryRequestsFundament


NO_PENDING_ACCOUNT_RECOVERY_MESSAGE: Final[str] = "No pending account recovery request."


@dataclass(kw_only=True)
class ShowPendingAccountRecovery(WorldBasedCommand):
    account_name: str
    _result: FindAccountRecoveryRequests = field(init=False)

    async def fetch_data(self) -> None:
        self._result = await self.world.node.api.database_api.find_account_recovery_requests(
            accounts=[self.account_name]
        )

    async def _run(self) -> None:
        requests = self._result.requests
        if requests:
            table = self._create_table(requests)
            print_cli(table)
            return
        print_content_not_available(NO_PENDING_ACCOUNT_RECOVERY_MESSAGE)

    def _create_table(self, requests: list[FindAccountRecoveryRequestsFundament]) -> Table:
        title = self._format_table_title(self.account_name)
        table = Table(title=title, min_width=len(title))
        table.add_column("Account to recover")
        table.add_column("New owner key(s)")
        table.add_column("Expires")

        for request in requests:
            key_auths_str = ", ".join(f"{key} (w={weight})" for key, weight in request.new_owner_authority.key_auths)
            table.add_row(
                str(request.account_to_recover),
                key_auths_str,
                humanize_datetime(request.expires),
            )
        return table

    @classmethod
    def _format_table_title(cls, account_name: str) -> str:
        return f"Pending account recovery requests for `{account_name}`"
