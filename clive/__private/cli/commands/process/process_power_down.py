from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import PowerDownInProgressError
from clive.__private.core.hive_vests_conversions import hive_to_vests
from clive.models import Asset
from schemas.operations import WithdrawVestingOperation

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.hive_power_data import HivePowerData


@dataclass(kw_only=True)
class ProcessPowerDown(OperationCommand):
    account_name: str
    amount: Asset.VotingT
    only_new_power_down: bool = False

    async def _create_operation(self) -> WithdrawVestingOperation:
        if self.only_new_power_down:
            wrapper = await self.world.commands.retrieve_hp_data(account_name=self.account_name)
            hp_data = wrapper.result_or_raise
            self.assert_no_pending_power_down(hp_data)

        vesting_shares: Asset.Vests
        if isinstance(self.amount, Asset.Hive):
            gdpo = await self.world.app_state.get_dynamic_global_properties()
            vesting_shares = hive_to_vests(self.amount, gdpo)
        else:
            vesting_shares = self.amount

        return WithdrawVestingOperation(
            account=self.account_name,
            vesting_shares=vesting_shares,
        )

    def assert_no_pending_power_down(self, hp_data: HivePowerData) -> None:
        if hp_data.to_withdraw.vests_balance != Asset.vests(0):
            raise PowerDownInProgressError
