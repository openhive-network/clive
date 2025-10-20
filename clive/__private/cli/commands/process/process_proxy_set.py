from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.models.schemas import AccountWitnessProxyOperation

if TYPE_CHECKING:
    from clive.__private.cli.types import ComposeTransaction


@dataclass(kw_only=True)
class ProcessProxySet(OperationCommand):
    account_name: str
    proxy: str

    async def _create_operations(self) -> ComposeTransaction:
        yield AccountWitnessProxyOperation(
            account=self.account_name,
            proxy=self.proxy,
        )
