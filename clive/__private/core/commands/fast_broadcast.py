from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_in_active import CommandInActive
from clive.__private.core.commands.perform_actions_on_transaction import PerformActionsOnTransaction

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper
    from clive.__private.core.keys import PublicKey
    from clive.__private.core.node.node import Node
    from clive.models import Operation


@dataclass(kw_only=True)
class FastBroadcast(CommandInActive):
    node: Node
    operation: Operation
    beekeeper: Beekeeper
    sign_with: PublicKey

    async def _execute(self) -> None:
        await PerformActionsOnTransaction(
            content=self.operation,
            app_state=self.app_state,
            node=self.node,
            beekeeper=self.beekeeper,
            sign_key=self.sign_with,
            save_file_path=None,
            broadcast=True,
        ).execute()
