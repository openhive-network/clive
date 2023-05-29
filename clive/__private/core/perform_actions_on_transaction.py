from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.commands.broadcast import Broadcast
from clive.__private.core.commands.save_binary import SaveToFileAsBinary
from clive.__private.core.commands.sign import Sign
from clive.__private.core.ensure_transaction import ensure_transaction

if TYPE_CHECKING:
    from pathlib import Path

    from clive.__private.core.beekeeper import Beekeeper
    from clive.__private.core.ensure_transaction import TransactionConvertibleType
    from clive.__private.core.node.node import Node
    from clive.__private.storage.mock_database import PrivateKeyAlias


def perform_actions_on_transaction(
    content: TransactionConvertibleType,
    *,
    node: Node,
    beekeeper: Beekeeper,
    chain_id: str,
    sign_key: PrivateKeyAlias | None = None,
    save_file_path: Path | None = None,
    broadcast: bool = False,
) -> None:
    """This function performs commands on a transaction object.

    Args:
        content: The content to be converted to a transaction.
            (This can be a transaction object, a list of operations, or a single operation.)
        node: The node which will be used for transaction broadcasting.
        beekeeper: The beekeeper to use to sign the transaction.
        sign_key: The private key to sign the transaction with. If not provided, the transaction will not be signed.
        save_file_path: The path to save the transaction to. If not provided, the transaction will not be saved.
        broadcast: Whether to broadcast the transaction.
    """
    transaction = ensure_transaction(content, node=node)

    if sign_key:
        transaction = Sign(
            beekeeper=beekeeper, transaction=transaction, key=sign_key, chain_id=chain_id
        ).execute_with_result()

    if save_file_path:
        SaveToFileAsBinary(transaction=transaction, file_path=save_file_path).execute()

    if transaction.is_signed() and broadcast:
        Broadcast(node=node, transaction=transaction).execute()
