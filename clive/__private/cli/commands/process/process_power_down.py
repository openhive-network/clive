from __future__ import annotations

from dataclasses import dataclass, field

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import PowerDownInProgressError
from clive.__private.core.constants.node import VESTS_TO_REMOVE_POWER_DOWN
from clive.__private.core.ensure_vests import ensure_vests_async
from clive.__private.models.asset import Asset
from clive.__private.models.schemas import WithdrawVestingOperation


@dataclass(kw_only=True)
class ProcessPowerDown(OperationCommand):
    account_name: str
    amount: Asset.VotingT

    async def _create_operation(self) -> WithdrawVestingOperation:
        vesting_shares = await ensure_vests_async(self.amount, self.world)

        return WithdrawVestingOperation(
            account=self.account_name,
            vesting_shares=vesting_shares,
        )


@dataclass(kw_only=True)
class ProcessPowerDownStart(ProcessPowerDown):
    async def validate_inside_context_manager(self) -> None:
        await self._validate_no_pending_power_down()
        await super().validate_inside_context_manager()

    async def _validate_no_pending_power_down(self) -> None:
        wrapper = await self.world.commands.retrieve_hp_data(account_name=self.account_name)
        hp_data = wrapper.result_or_raise
        if hp_data.to_withdraw.vests_balance != Asset.vests(0):
            raise PowerDownInProgressError


@dataclass(kw_only=True)
class ProcessPowerDownCancel(ProcessPowerDown):
    amount: Asset.VotingT = field(init=False, default_factory=lambda: Asset.vests(VESTS_TO_REMOVE_POWER_DOWN))
