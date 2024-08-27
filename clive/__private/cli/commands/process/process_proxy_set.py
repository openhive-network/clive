from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.models.schemas import AccountWitnessProxyOperation


@dataclass(kw_only=True)
class ProcessProxySet(OperationCommand):
    account_name: str
    proxy: str

    async def _create_operation(self) -> AccountWitnessProxyOperation:
        return AccountWitnessProxyOperation(
            account=self.account_name,
            proxy=self.proxy,
        )
