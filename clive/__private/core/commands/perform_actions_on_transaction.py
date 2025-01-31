from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.commands.broadcast import Broadcast
from clive.__private.core.commands.build_transaction import BuildTransaction
from clive.__private.core.commands.save_transaction import SaveTransaction
from clive.__private.core.commands.sign import ALREADY_SIGNED_MODE_DEFAULT, AlreadySignedMode, Sign
from clive.__private.core.commands.unsign import UnSign
from clive.__private.models import Transaction

if TYPE_CHECKING:
    from beekeepy import AsyncUnlockedWallet

    from clive.__private.core.app_state import AppState


if TYPE_CHECKING:
    from pathlib import Path

    from clive.__private.core.ensure_transaction import TransactionConvertibleType
    from clive.__private.core.keys import PublicKey
    from clive.__private.core.node import Node


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
    already_signed_mode: How to handle the situation when transaction is already signed.
    force_unsign: Whether to remove the signature from the transaction. Even when sign_key is provided.
    chain_id: The chain ID to use when signing the transaction. If not provided, the one from the profile and
        then from the node get_config api will be used as fallback.
    save_file_path: The path to save the transaction to. If not provided, the transaction will not be saved.
        Format is determined by the file extension. (e.g. `.json` for JSON, `.bin` for binary, if none of these - JSON)
    broadcast: Whether to broadcast the transaction.

    Returns:
    -------
    The transaction object.
    """

    content: TransactionConvertibleType
    app_state: AppState
    node: Node
    unlocked_wallet: AsyncUnlockedWallet | None = None
    """Required if transaction needs to be signed - when sign_key is provided."""
    sign_key: PublicKey | None = None
    already_signed_mode: AlreadySignedMode = ALREADY_SIGNED_MODE_DEFAULT
    force_unsign: bool = False
    chain_id: str | None = None
    save_file_path: Path | None = None
    force_save_format: Literal["json", "bin"] | None = None
    broadcast: bool = False

    async def _execute(self) -> None:
        transaction = await BuildTransaction(content=self.content, node=self.node).execute_with_result()

        if self.sign_key and not self.force_unsign:
            assert self.unlocked_wallet is not None, "wallet is required when sign_key is provided"

            transaction = await Sign(
                unlocked_wallet=self.unlocked_wallet,
                transaction=transaction,
                key=self.sign_key,
                chain_id=self.chain_id or await self.node.chain_id,
                already_signed_mode=self.already_signed_mode,
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
