from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.command import Command
from clive.__private.core.perform_actions_on_transaction import perform_actions_on_transaction

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper
    from clive.__private.storage.mock_database import PrivateKeyAlias
    from clive.core.url import Url
    from clive.models.operation import Operation


@dataclass
class FastBroadcast(Command[None]):
    operation: Operation
    beekeeper: Beekeeper
    sign_with: PrivateKeyAlias
    node_address: Url

    def execute(self) -> None:
        perform_actions_on_transaction(
            content=self.operation,
            beekeeper=self.beekeeper,
            node_address=self.node_address,
            sign_key=self.sign_with,
            save_file_path=None,
            broadcast=True,
        )
