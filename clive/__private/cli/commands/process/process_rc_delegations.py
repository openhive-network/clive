from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.core.ensure_vests import ensure_vests_async
from clive.__private.core.wax_operation_wrapper import WaxRcDelegationWrapper
from clive.__private.models.schemas import CustomJsonOperation

if TYPE_CHECKING:
    from clive.__private.cli.types import ComposeTransaction
    from clive.__private.models.asset import Asset


@dataclass(kw_only=True)
class ProcessRcDelegation(OperationCommand):
    from_account: str
    delegatee: str
    amount: Asset.VotingT

    async def _create_operations(self) -> ComposeTransaction:
        vesting_shares = await ensure_vests_async(self.amount, self.world)
        wrapper = WaxRcDelegationWrapper.create_delegation(
            from_account=self.from_account, delegatee=self.delegatee, max_rc=vesting_shares.amount
        )
        yield wrapper.to_schemas(self.world.wax_interface, CustomJsonOperation)


@dataclass(kw_only=True)
class ProcessRcDelegationRemove(OperationCommand):
    from_account: str
    delegatee: str

    async def _create_operations(self) -> ComposeTransaction:
        wrapper = WaxRcDelegationWrapper.create_removal(from_account=self.from_account, delegatee=self.delegatee)
        yield wrapper.to_schemas(self.world.wax_interface, CustomJsonOperation)
