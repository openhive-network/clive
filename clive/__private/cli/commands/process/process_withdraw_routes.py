from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import WithdrawRoutesZeroPercentError
from clive.__private.core.constants.node import PERCENT_TO_REMOVE_WITHDRAW_ROUTE
from clive.__private.core.percent_conversions import percent_to_hive_percent
from clive.__private.models.schemas import SetWithdrawVestingRouteOperation


@dataclass(kw_only=True)
class ProcessWithdrawRoutes(OperationCommand):
    """
    Class to handle the processing of withdraw vesting routes.

    Args:
        from_account: The account from which the withdraw route is set.
        to_account: The account to which the withdraw route is set.
        percent: The percentage of vesting shares to withdraw.
        auto_vest: Whether to automatically vest the shares.
    """

    from_account: str
    to_account: str
    percent: Decimal
    auto_vest: bool

    async def validate(self) -> None:
        """
        Validate the parameters for setting withdraw vesting routes.

        Returns:
            None
        """
        await self._validate_percent()
        await super().validate()

    async def _create_operation(self) -> SetWithdrawVestingRouteOperation:
        """
        Create the operation for setting withdraw vesting routes.

        Returns:
            SetWithdrawVestingRouteOperation: The operation to be executed.
        """
        return SetWithdrawVestingRouteOperation(
            from_account=self.from_account,
            to_account=self.to_account,
            percent=percent_to_hive_percent(self.percent),
            auto_vest=self.auto_vest,
        )

    async def _validate_percent(self) -> None:
        """
        Validate the percent value for withdraw routes.

        Raises:
            WithdrawRoutesZeroPercentError: If the percent is set to zero.

        Returns:
            None
        """
        if self.percent == PERCENT_TO_REMOVE_WITHDRAW_ROUTE:
            raise WithdrawRoutesZeroPercentError


@dataclass(kw_only=True)
class ProcessWithdrawRoutesRemove(ProcessWithdrawRoutes):
    """
    Class to handle the removal of withdraw vesting routes.

    Args:
        from_account: The account from which the withdraw route is removed.
        to_account: The account to which the withdraw route is removed.
    """

    percent: Decimal = field(init=False, default_factory=lambda: Decimal(PERCENT_TO_REMOVE_WITHDRAW_ROUTE))
    auto_vest: bool = field(init=False, default=False)

    async def _validate_percent(self) -> None:
        """
        Validate the percent value for removing withdraw routes.

        Returns:
            None
        """
