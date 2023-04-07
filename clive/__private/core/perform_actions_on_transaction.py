from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.commands.broadcast import Broadcast
from clive.__private.core.commands.save import SaveToFile
from clive.__private.core.commands.sign import Sign
from clive.__private.core.ensure_transaction import ensure_transaction

if TYPE_CHECKING:
    from pathlib import Path

    from clive.__private.core.ensure_transaction import TransactionConvertibleType
    from clive.__private.storage.mock_database import PrivateKey


def perform_actions_on_transaction(
    content: TransactionConvertibleType,
    *,
    sign_key: PrivateKey | None = None,
    save_file_path: Path | None = None,
    broadcast: bool = False,
) -> None:
    """This function performs commands on a transaction object.

    Args:
        content: The content to be converted to a transaction.
            (This can be a transaction object, a list of operations, or a single operation.)
        sign_key: The private key to sign the transaction with. If not provided, the transaction will not be signed.
        save_file_path: The path to save the transaction to. If not provided, the transaction will not be saved.
        broadcast: Whether to broadcast the transaction.
    """
    transaction = ensure_transaction(content)

    if sign_key:
        Sign(transaction, key=sign_key).execute()

    if save_file_path:
        SaveToFile(transaction, save_file_path).execute()

    if transaction.signed and broadcast:
        Broadcast(transaction).execute()
