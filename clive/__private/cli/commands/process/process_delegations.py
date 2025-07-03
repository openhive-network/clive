from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import DelegationsZeroAmountError
from clive.__private.core.constants.node_special_assets import DELEGATION_REMOVE_ASSETS
from clive.__private.core.ensure_vests import ensure_vests_async
from clive.__private.models.schemas import DelegateVestingSharesOperation

if TYPE_CHECKING:
    from clive.__private.models.asset import Asset


@dataclass(kw_only=True)
class ProcessDelegations(OperationCommand):
    """
    Class to handle delegation operations in the Steem blockchain.

    Args:
        delegator: The account delegating the vesting shares.
        delegatee: The account receiving the delegated vesting shares.
        amount: The amount of vesting shares to delegate.
    """

    delegator: str
    delegatee: str
    amount: Asset.VotingT

    async def validate(self) -> None:
        """
        Validate the delegation operation.

        Returns:
            None
        """
        await self._validate_amount()
        await super().validate()

    async def _create_operation(self) -> DelegateVestingSharesOperation:
        """
        Create the operation for delegating vesting shares.

        Returns:
            DelegateVestingSharesOperation: The operation to be executed.
        """
        vesting_shares = await ensure_vests_async(self.amount, self.world)

        return DelegateVestingSharesOperation(
            delegator=self.delegator,
            delegatee=self.delegatee,
            vesting_shares=vesting_shares,
        )

    async def _validate_amount(self) -> None:
        """
        Validate the amount of vesting shares to be delegated.

        Raises:
            DelegationsZeroAmountError: If the amount is zero or in the remove assets list.

        Returns:
            None
        """
        if self.amount in DELEGATION_REMOVE_ASSETS:
            raise DelegationsZeroAmountError


@dataclass(kw_only=True)
class ProcessDelegationsRemove(ProcessDelegations):
    """
    Class to handle the removal of delegated vesting shares.

    Args:
        amount: The amount of vesting shares to remove, set to a default value.
    """

    amount: Asset.VotingT = field(init=False, default_factory=lambda: DELEGATION_REMOVE_ASSETS[1].copy())

    async def _validate_amount(self) -> None:
        """
        Skip the amount validation as it is already set.

        Returns:
            None
        """
