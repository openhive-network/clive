from __future__ import annotations

from dataclasses import dataclass, field

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import DelegationsZeroAmountError
from clive.__private.core.constants import VESTS_REMOVE_DELEGATION_AMOUNT
from clive.__private.core.ensure_vests import ensure_vests_async
from clive.models.asset import Asset
from schemas.operations import DelegateVestingSharesOperation


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
        if self.amount == Asset.vests(VESTS_REMOVE_DELEGATION_AMOUNT) or self.amount == Asset.hive(
            VESTS_REMOVE_DELEGATION_AMOUNT
        ):
            raise DelegationsZeroAmountError


@dataclass(kw_only=True)
class ProcessDelegationsRemove(ProcessDelegations):
    amount: Asset.VotingT = field(init=False, default_factory=lambda: Asset.vests(VESTS_REMOVE_DELEGATION_AMOUNT))

    async def _validate_amount(self) -> None:
        """Skip the amount validation as it is already set."""
