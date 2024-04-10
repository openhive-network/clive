from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.commands.find_accounts import AccountNotFoundError, FindAccounts

if TYPE_CHECKING:
    from clive.__private.core.node import Node


@dataclass(kw_only=True)
class DoesAccountExistsInNode(CommandWithResult[bool]):
    node: Node
    account_name: str

    async def _execute(self) -> None:
        try:
            await FindAccounts(node=self.node, accounts=[self.account_name]).execute()
        except AccountNotFoundError:
            self._result = False
        else:
            self._result = True
