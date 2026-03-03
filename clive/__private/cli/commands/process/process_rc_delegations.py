from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import (
    RcDelegationBelowMinimumError,
    RcDelegationInsufficientRcError,
    RcDelegationSameAmountError,
)
from clive.__private.core import iwax
from clive.__private.core.ensure_vests import ensure_vests_async
from clive.__private.core.wax_operation_wrapper import WaxRcDelegationWrapper
from clive.__private.models.asset import Asset
from clive.__private.models.schemas import CustomJsonOperation

if TYPE_CHECKING:
    from clive.__private.cli.types import ComposeTransaction
    from clive.__private.core.commands.data_retrieval.rc_data import RcData


@dataclass(kw_only=True)
class ProcessRcDelegation(OperationCommand):
    from_account: str
    delegatee: str
    amount: Asset.VotingT
    _rc_data: RcData = field(init=False)
    _vesting_shares: Asset.Vests = field(init=False)

    async def fetch_data(self) -> None:
        await super().fetch_data()
        self._rc_data = (await self.world.commands.retrieve_rc_data(account_name=self.from_account)).result_or_raise
        self._vesting_shares = await ensure_vests_async(self.amount, self.world)

    async def validate_inside_context_manager(self) -> None:
        await self._validate_rc_delegation()
        await super().validate_inside_context_manager()

    async def _validate_rc_delegation(self) -> None:
        rc_data = self._rc_data
        amount_in_rc = int(self._vesting_shares.amount)

        amount_hp: Asset.Hive
        if isinstance(self.amount, Asset.Hive):
            amount_hp = self.amount
        else:
            amount_hp = iwax.calculate_vests_to_hp(amount_in_rc, rc_data.gdpo)

        if amount_in_rc < rc_data.min_rc_delegation:
            raise RcDelegationBelowMinimumError(
                amount_hp,
                self._vesting_shares,
                iwax.calculate_vests_to_hp(rc_data.min_rc_delegation, rc_data.gdpo),
                iwax.vests(rc_data.min_rc_delegation),
            )

        existing_delegation = next((d for d in rc_data.outgoing_delegations if str(d.to) == self.delegatee), None)
        if existing_delegation is not None and int(existing_delegation.delegated_rc) == amount_in_rc:
            raise RcDelegationSameAmountError(
                self.delegatee,
                iwax.calculate_vests_to_hp(amount_in_rc, rc_data.gdpo),
                iwax.vests(amount_in_rc),
            )

        existing_amount = int(existing_delegation.delegated_rc) if existing_delegation is not None else 0
        # Mirror the node check: from_delegable_rc >= delta_total
        from_delegable_rc = rc_data.current_mana - (rc_data.delegated_rc - existing_amount)
        delta_total = amount_in_rc - existing_amount
        if delta_total > from_delegable_rc:
            max_delegable = max(from_delegable_rc + existing_amount, 0)
            raise RcDelegationInsufficientRcError(
                amount_hp,
                self._vesting_shares,
                iwax.calculate_vests_to_hp(max_delegable, rc_data.gdpo),
                iwax.vests(max_delegable),
            )

    async def _create_operations(self) -> ComposeTransaction:
        wrapper = WaxRcDelegationWrapper.create_delegation(
            from_account=self.from_account, delegatee=self.delegatee, max_rc=self._vesting_shares.amount
        )
        yield wrapper.to_schemas(self.world.wax_interface, CustomJsonOperation)


@dataclass(kw_only=True)
class ProcessRcDelegationRemove(OperationCommand):
    from_account: str
    delegatee: str

    async def _create_operations(self) -> ComposeTransaction:
        wrapper = WaxRcDelegationWrapper.create_removal(from_account=self.from_account, delegatee=self.delegatee)
        yield wrapper.to_schemas(self.world.wax_interface, CustomJsonOperation)
