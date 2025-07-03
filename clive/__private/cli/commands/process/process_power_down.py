from __future__ import annotations

from dataclasses import dataclass, field

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import PowerDownInProgressError
from clive.__private.core.constants.node_special_assets import POWER_DOWN_REMOVE_ASSET
from clive.__private.core.ensure_vests import ensure_vests_async
from clive.__private.models.asset import Asset
from clive.__private.models.schemas import WithdrawVestingOperation


@dataclass(kw_only=True)
class ProcessPowerDown(OperationCommand):
    """
    Class to handle the power down process in the Hive blockchain.

    Args:
        account_name: The name of the account initiating the power down.
        amount: The amount of vesting shares to withdraw.
    """

    account_name: str
    amount: Asset.VotingT

    async def _create_operation(self) -> WithdrawVestingOperation:
        """
        Create an operation to withdraw vesting shares.

        Returns:
            WithdrawVestingOperation: The operation to withdraw vesting shares.
        """
        vesting_shares = await ensure_vests_async(self.amount, self.world)

        return WithdrawVestingOperation(
            account=self.account_name,
            vesting_shares=vesting_shares,
        )


@dataclass(kw_only=True)
class ProcessPowerDownStart(ProcessPowerDown):
    """Class to initiate the power down process in the Hive blockchain."""

    async def validate_inside_context_manager(self) -> None:
        """
        Validate that there is no pending power down before starting a new one.

        Returns:
            None
        """
        await self._validate_no_pending_power_down()
        await super().validate_inside_context_manager()

    async def _validate_no_pending_power_down(self) -> None:
        """
        Check if there is an ongoing power down process for the account.

        Raises:
            PowerDownInProgressError: If there is an ongoing power down process.

        Returns:
            None
        """
        wrapper = await self.world.commands.retrieve_hp_data(account_name=self.account_name)
        hp_data = wrapper.result_or_raise
        if hp_data.to_withdraw.vests_balance != Asset.vests(0):
            raise PowerDownInProgressError


@dataclass(kw_only=True)
class ProcessPowerDownCancel(ProcessPowerDown):
    """
    Class to cancel an ongoing power down process in the Hive blockchain.

    Args:
        amount: The amount of vesting shares to remove from the power down.
    """

    amount: Asset.VotingT = field(init=False, default_factory=lambda: POWER_DOWN_REMOVE_ASSET.copy())
