from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.commands import execute_with_result
from clive.__private.core.commands.broadcast import Broadcast
from clive.__private.core.commands.save import SaveToFile
from clive.__private.core.commands.sign import Sign
from clive.__private.core.ensure_transaction import ensure_transaction

if TYPE_CHECKING:
    from pathlib import Path

    from clive.__private.core.beekeeper import BeekeeperRemote
    from clive.__private.core.ensure_transaction import TransactionConvertibleType
    from clive.__private.storage.mock_database import PrivateKeyAlias
    from clive.core.url import Url


def perform_actions_on_transaction(
    content: TransactionConvertibleType,
    *,
    beekeeper: BeekeeperRemote,
    node_address: Url,
    sign_key: PrivateKeyAlias | None = None,
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
        transaction = execute_with_result(Sign(beekeeper=beekeeper, transaction=transaction, key=sign_key))

    if save_file_path:
        SaveToFile(transaction=transaction, file_path=save_file_path).execute()

    if transaction.signed and broadcast:
        Broadcast(node_address=node_address, transaction=transaction).execute()
