from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import Command
from clive.__private.core.perform_actions_on_transaction import perform_actions_on_transaction

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper
    from clive.__private.core.keys.keys import PublicKey
    from clive.__private.core.node.node import Node
    from clive.models import Operation


@dataclass(kw_only=True)
class FastBroadcast(Command):
    node: Node
    operation: Operation
    beekeeper: Beekeeper
    sign_with: PublicKey
    chain_id: str

    def _execute(self) -> None:
        perform_actions_on_transaction(
            content=self.operation,
            node=self.node,
            beekeeper=self.beekeeper,
            chain_id=self.chain_id,
            sign_key=self.sign_with,
            save_file_path=None,
            broadcast=True,
        )
