from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.commands.broadcast import Broadcast
from clive.__private.core.commands.save_transaction import SaveTransaction
from clive.__private.core.commands.sign import Sign
from clive.__private.core.commands.unsign import UnSign
from clive.__private.core.ensure_transaction import ensure_transaction
from clive.models import Transaction

if TYPE_CHECKING:
    from clive.__private.core.commands.abc.command_in_active import AppStateProtocol

if TYPE_CHECKING:
    from pathlib import Path

    from clive.__private.core.beekeeper import Beekeeper
    from clive.__private.core.ensure_transaction import TransactionConvertibleType
    from clive.__private.core.keys import PublicKey
    from clive.__private.core.node.node import Node


@dataclass(kw_only=True)
class PerformActionsOnTransaction(CommandWithResult[Transaction]):
    """
    Performs commands on a transaction object.

    Args:
    ----
    content: The content to be converted to a transaction.
        (This can be a transaction object, a list of operations, or a single operation.)
    app_state: The app state.
    node: The node which will be used for transaction broadcasting.
    beekeeper: The beekeeper to use to sign the transaction.
    sign_key: The private key to sign the transaction with. If not provided, the transaction will not be signed.
    force_unsign: Whether to remove the signature from the transaction. Even when sign_key is provided.
    save_file_path: The path to save the transaction to. If not provided, the transaction will not be saved.
        Format is determined by the file extension. (e.g. `.json` for JSON, `.bin` for binary, if none of these - JSON)
    broadcast: Whether to broadcast the transaction.

    Returns:
    -------
    The transaction object.
    """

    content: TransactionConvertibleType
    app_state: AppStateProtocol
    node: Node
    beekeeper: Beekeeper
    sign_key: PublicKey | None = None
    force_unsign: bool = False
    save_file_path: Path | None = None
    force_save_format: Literal["json", "bin"] | None = None
    broadcast: bool = False

    async def _execute(self) -> None:
        transaction = await ensure_transaction(self.content, node=self.node)

        if self.sign_key and not self.force_unsign:
            transaction = await Sign(
                app_state=self.app_state,
                beekeeper=self.beekeeper,
                transaction=transaction,
                key=self.sign_key,
                chain_id=await self.node.chain_id,
            ).execute_with_result()

        if self.force_unsign:
            transaction = await UnSign(transaction=transaction).execute_with_result()

        if path := self.save_file_path:
            await SaveTransaction(
                transaction=transaction, file_path=path, force_format=self.force_save_format
            ).execute()

        if self.broadcast:
            await Broadcast(node=self.node, transaction=transaction).execute()

        self._result = transaction
