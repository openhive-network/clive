from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from schemas.operations import SetWithdrawVestingRouteOperation


@dataclass(kw_only=True)
class ProcessWithdrawRoutes(OperationCommand):
    from_account: str
    to_account: str
    percent: float
    auto_vest: bool

    async def _create_operation(self) -> SetWithdrawVestingRouteOperation:
        return SetWithdrawVestingRouteOperation(
            from_account=self.from_account,
            to_account=self.to_account,
            percent=int(self.percent * 100),
            auto_vest=self.auto_vest,
        )
