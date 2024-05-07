from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import CommandError
from clive.__private.core.commands.abc.command_data_retrieval import CommandDataRetrieval
from clive.models.aliased import FindVestingDelegationExpirations as SchemasFindVestingDelegationExpirations
from clive.models.aliased import VestingDelegationExpiration

if TYPE_CHECKING:
    from clive.__private.core.node.node import Node


class FindVestingDelegationExpirationsCommandError(CommandError):
    pass


@dataclass(kw_only=True)
class FindVestingDelegationExpirations(
    CommandDataRetrieval[
        SchemasFindVestingDelegationExpirations,
        SchemasFindVestingDelegationExpirations,
        list[VestingDelegationExpiration],
    ]
):
    node: Node
    account: str

    async def _harvest_data_from_api(self) -> SchemasFindVestingDelegationExpirations:
        return await self.node.api.database_api.find_vesting_delegation_expirations(account=self.account)

    async def _sanitize_data(
        self, data: SchemasFindVestingDelegationExpirations
    ) -> SchemasFindVestingDelegationExpirations:
        self._assert_delegator(data)
        return data

    async def _process_data(self, data: SchemasFindVestingDelegationExpirations) -> list[VestingDelegationExpiration]:
        return data.delegations

    def _assert_delegator(self, response: SchemasFindVestingDelegationExpirations) -> None:
        for delegation in response.delegations:
            if delegation.delegator != self.account:
                raise FindVestingDelegationExpirationsCommandError(self, f"Wrong delegator in delegation {delegation}")
