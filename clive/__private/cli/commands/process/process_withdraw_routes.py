from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.core.percent_conversions import percent_to_hive_percent
from schemas.operations import SetWithdrawVestingRouteOperation

if TYPE_CHECKING:
    from decimal import Decimal


@dataclass(kw_only=True)
class ProcessWithdrawRoutes(OperationCommand):
    from_account: str
    to_account: str
    percent: Decimal
    auto_vest: bool

    async def _create_operation(self) -> SetWithdrawVestingRouteOperation:
        return SetWithdrawVestingRouteOperation(
            from_account=self.from_account,
            to_account=self.to_account,
            percent=percent_to_hive_percent(self.percent),
            auto_vest=self.auto_vest,
        )
