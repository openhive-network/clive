from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import CommandError
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.models.aliased import FindVestingDelegationExpirations as SchemasFindVestingDelegationExpirations
from clive.models.aliased import SchemasVestingDelegationExpirations

if TYPE_CHECKING:
    from clive.__private.core.node.node import Node


class FindVestingDelegationExpirationsCommandError(CommandError):
    pass


@dataclass(kw_only=True)
class FindVestingDelegationExpirations(CommandWithResult[list[SchemasVestingDelegationExpirations]]):
    node: Node
    account: str

    async def _execute(self) -> None:
        response: SchemasFindVestingDelegationExpirations = (
            await self.node.api.database_api.find_vesting_delegation_expirations(account=self.account)
        )
        self._check_delegator(response)
        self._result = response.delegations

    def _check_delegator(self, response: SchemasFindVestingDelegationExpirations) -> None:
        for delegation in response.delegations:
            if delegation.delegator != self.account:
                raise FindVestingDelegationExpirationsCommandError(self, f"Wrong delegator in delegation {delegation}")
