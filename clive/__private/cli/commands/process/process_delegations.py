from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.core.hive_vests_conversions import hive_to_vests
from clive.models import Asset
from schemas.operations import DelegateVestingSharesOperation


@dataclass(kw_only=True)
class ProcessDelegations(OperationCommand):
    delegator: str
    delegatee: str
    amount: Asset.VotingT = Asset.vests(0)

    async def _create_operation(self) -> DelegateVestingSharesOperation:
        vesting_shares: Asset.Vests
        if isinstance(self.amount, Asset.Hive):
            gdpo = await self.world.node.api.database_api.get_dynamic_global_properties()
            vesting_shares = hive_to_vests(self.amount, gdpo)
        else:
            vesting_shares = self.amount

        return DelegateVestingSharesOperation(
            delegator=self.delegator,
            delegatee=self.delegatee,
            vesting_shares=vesting_shares,
        )
