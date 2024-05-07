from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import WithdrawRoutesZeroPercentError
from clive.__private.core.constants import PERCENT_REMOVE_WITHDRAW_ROUTE_AMOUNT
from clive.__private.core.percent_conversions import percent_to_hive_percent
from schemas.operations import SetWithdrawVestingRouteOperation


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

    async def validate(self) -> None:
        await self._validate_percent()
        await super().validate()

    async def _validate_percent(self) -> None:
        if self.percent == 0:
            raise WithdrawRoutesZeroPercentError


@dataclass(kw_only=True)
class ProcessWithdrawRoutesRemove(ProcessWithdrawRoutes):
    percent: Decimal = field(init=False, default_factory=lambda: Decimal(PERCENT_REMOVE_WITHDRAW_ROUTE_AMOUNT))
    auto_vest: bool = field(init=False, default=False)

    async def _validate_percent(self) -> None:
        pass
