from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import DelegationsZeroAmountError
from clive.__private.core.constants.node_special_assets import DELEGATIONS_REMOVE_ASSETS
from clive.__private.core.ensure_vests import ensure_vests_async
from clive.__private.models.schemas import DelegateVestingSharesOperation

if TYPE_CHECKING:
    from clive.__private.models.asset import Asset


@dataclass(kw_only=True)
class ProcessDelegations(OperationCommand):
    delegator: str
    delegatee: str
    amount: Asset.VotingT

    async def _create_operation(self) -> DelegateVestingSharesOperation:
        vesting_shares = await ensure_vests_async(self.amount, self.world)

        return DelegateVestingSharesOperation(
            delegator=self.delegator,
            delegatee=self.delegatee,
            vesting_shares=vesting_shares,
        )

    async def validate(self) -> None:
        await self._validate_amount()
        await super().validate()

    async def _validate_amount(self) -> None:
        if self.amount in DELEGATIONS_REMOVE_ASSETS:
            raise DelegationsZeroAmountError


@dataclass(kw_only=True)
class ProcessDelegationsRemove(ProcessDelegations):
    amount: Asset.VotingT = field(init=False, default_factory=lambda: DELEGATIONS_REMOVE_ASSETS[1])

    async def _validate_amount(self) -> None:
        """Skip the amount validation as it is already set."""
