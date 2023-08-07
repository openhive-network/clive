from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.commands.broadcast import Broadcast
from clive.__private.core.commands.save_binary import SaveToFileAsBinary
from clive.__private.core.commands.sign import Sign
from clive.__private.core.ensure_transaction import ensure_transaction

if TYPE_CHECKING:
    from clive.__private.core.commands.abc.command_in_active import AppStateProtocol
    from clive.models import Transaction

if TYPE_CHECKING:
    from pathlib import Path

    from clive.__private.core.beekeeper import Beekeeper
    from clive.__private.core.ensure_transaction import TransactionConvertibleType
    from clive.__private.core.keys import PublicKey
    from clive.__private.core.node.node import Node


async def perform_actions_on_transaction(  # noqa: PLR0913
    content: TransactionConvertibleType,
    *,
    app_state: AppStateProtocol,
    node: Node,
    beekeeper: Beekeeper,
    chain_id: str,
    sign_key: PublicKey | None = None,
    save_file_path: Path | None = None,
    broadcast: bool = False,
) -> Transaction:
    """
    Performs commands on a transaction object.

    Args:
    ----
    content: The content to be converted to a transaction.
        (This can be a transaction object, a list of operations, or a single operation.)
    app_state: The app state.
    node: The node which will be used for transaction broadcasting.
    beekeeper: The beekeeper to use to sign the transaction.
    chain_id: The chain id to use for signing the transaction.
    sign_key: The private key to sign the transaction with. If not provided, the transaction will not be signed.
    save_file_path: The path to save the transaction to. If not provided, the transaction will not be saved.
    broadcast: Whether to broadcast the transaction.

    Returns:
    -------
    The transaction object.
    """
    transaction = await ensure_transaction(content, node=node)

    if sign_key:
        transaction = await Sign(
            app_state=app_state, beekeeper=beekeeper, transaction=transaction, key=sign_key, chain_id=chain_id
        ).async_execute_with_result()

    if save_file_path:
        await SaveToFileAsBinary(transaction=transaction, file_path=save_file_path).async_execute()

    if transaction.is_signed() and broadcast:
        await Broadcast(node=node, transaction=transaction).async_execute()

    return transaction
