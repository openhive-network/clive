from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_in_active import CommandInActive
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.commands.perform_actions_on_transaction import PerformActionsOnTransaction
from clive.models import Transaction

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper
    from clive.__private.core.ensure_transaction import TransactionConvertibleType
    from clive.__private.core.keys import PublicKey
    from clive.__private.core.node.node import Node


@dataclass(kw_only=True)
class FastBroadcast(CommandInActive, CommandWithResult[Transaction]):
    node: Node
    content: TransactionConvertibleType
    beekeeper: Beekeeper
    sign_with: PublicKey

    async def _execute(self) -> None:
        self._result = await PerformActionsOnTransaction(
            content=self.content,
            app_state=self.app_state,
            node=self.node,
            beekeeper=self.beekeeper,
            sign_key=self.sign_with,
            save_file_path=None,
            broadcast=True,
        ).execute_with_result()
