from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from beekeepy.exceptions import UnknownDecisionPathError

from clive.__private.core.commands.abc.command import CommandError
from clive.__private.core.commands.abc.command_data_retrieval import CommandDataRetrieval
from clive.__private.models import HpVestsBalance

if TYPE_CHECKING:
    from datetime import datetime

    from clive.__private.core.node import Node
    from clive.__private.models.schemas import DynamicGlobalProperties, VestingDelegationExpiration
    from clive.__private.models.schemas import (
        FindVestingDelegationExpirations as SchemasFindVestingDelegationExpirations,
    )


class FindVestingDelegationExpirationsCommandError(CommandError):
    pass


@dataclass
class HarvestedDataRaw:
    find_vesting_delegation_expirations: SchemasFindVestingDelegationExpirations
    dgpo: DynamicGlobalProperties


@dataclass
class SanitizedData:
    delegations: list[VestingDelegationExpiration]
    dgpo: DynamicGlobalProperties


@dataclass
class VestingDelegationExpirationData:
    delegator: str
    amount: HpVestsBalance
    expiration: datetime

    @classmethod
    def create(
        cls, schema: VestingDelegationExpiration, dgpo: DynamicGlobalProperties
    ) -> VestingDelegationExpirationData:
        return cls(
            delegator=schema.delegator,
            amount=HpVestsBalance.create(schema.vesting_shares, dgpo),
            expiration=schema.expiration.value,
        )


@dataclass(kw_only=True)
class FindVestingDelegationExpirations(
    CommandDataRetrieval[
        HarvestedDataRaw,
        SanitizedData,
        list[VestingDelegationExpirationData],
    ]
):
    node: Node
    account: str

    async def _harvest_data_from_api(self) -> HarvestedDataRaw:
        async with await self.node.batch() as node:
            vesting_delegation_expirations = await node.api.database_api.find_vesting_delegation_expirations(
                account=self.account
            )
            dgpo = await node.api.database_api.get_dynamic_global_properties()
            return HarvestedDataRaw(vesting_delegation_expirations, dgpo)
        raise UnknownDecisionPathError(f"{self.__class__.__name__}:_harvest_data_from_api")

    async def _sanitize_data(self, data: HarvestedDataRaw) -> SanitizedData:
        delegations = data.find_vesting_delegation_expirations.delegations
        self._assert_delegator(delegations)
        return SanitizedData(delegations=delegations, dgpo=data.dgpo)

    async def _process_data(self, data: SanitizedData) -> list[VestingDelegationExpirationData]:
        delegations = data.delegations
        dgpo = data.dgpo
        return [VestingDelegationExpirationData.create(delegation, dgpo) for delegation in delegations]

    def _assert_delegator(self, delegations: list[VestingDelegationExpiration]) -> None:
        for delegation in delegations:
            if delegation.delegator != self.account:
                raise FindVestingDelegationExpirationsCommandError(self, f"Wrong delegator in delegation {delegation}")
