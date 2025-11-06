from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, Literal

from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.commands.autosign import (
    AutoSign,
    TransactionAlreadySignedAutoSignError,
)
from clive.__private.core.commands.broadcast import Broadcast
from clive.__private.core.commands.build_transaction import BuildTransaction
from clive.__private.core.commands.save_transaction import SaveTransaction
from clive.__private.core.commands.sign import Sign
from clive.__private.core.commands.unsign import UnSign
from clive.__private.core.constants.data_retrieval import ALREADY_SIGNED_MODE_DEFAULT
from clive.__private.models.transaction import Transaction

if TYPE_CHECKING:
    from beekeepy import AsyncUnlockedWallet

    from clive.__private.core.app_state import AppState


if TYPE_CHECKING:
    from pathlib import Path

    from clive.__private.core.ensure_transaction import TransactionConvertibleType
    from clive.__private.core.keys import PublicKey
    from clive.__private.core.node import Node
    from clive.__private.core.types import AlreadySignedMode


class AutoSignSkippedWarning(Warning):
    """
    Raised when autosign is skipped because the transaction is already signed.

    Attributes:
        MESSAGE: The warning message.
    """

    MESSAGE: Final[str] = "Your transaction is already signed. Autosign will be skipped."

    def __init__(self) -> None:
        super().__init__(self.MESSAGE)


@dataclass(kw_only=True)
class PerformActionsOnTransaction(CommandWithResult[Transaction]):
    """
    Performs commands on a transaction object.

    Attributes:
        content: The content to be converted to a transaction.
            (This can be a transaction object, a list of operations, or a single operation.)
        app_state: The app state.
        node: The node used for transaction broadcasting.
        unlocked_wallet: Required if the transaction needs to be signed.
        sign_key: The private key to sign the transaction with. If not provided, the transaction will not be signed.
        sign_keys: Multiple private keys to sign the transaction with (for multi-signature).
            Cannot be used with sign_key or autosign.
        autosign: Whether to automatically sign the transaction.
        already_signed_mode: How to handle already signed transactions.
        force_unsign: Whether to remove the signature from the transaction. Even when sign_key is provided.
        chain_id: The chain ID to use when signing the transaction. If not provided, the one from the profile and
            then from the node get_config api will be used as fallback.
        save_file_path: The path to save the transaction to. If not provided, the transaction will not be saved.
            Format is determined by file extension. (e.g. `.json` for JSON, `.bin` for binary, if none of these - JSON)
        force_save_format: The format to force when saving. Matters only when save_file_path is specified.
        broadcast: Whether to broadcast the transaction.

    Returns:
    The transaction object.
    """

    content: TransactionConvertibleType
    app_state: AppState
    node: Node
    unlocked_wallet: AsyncUnlockedWallet | None = None
    """Required if transaction needs to be signed - when sign_key/sign_keys is provided."""
    sign_key: PublicKey | None = None
    sign_keys: list[PublicKey] | None = None
    autosign: bool = False
    already_signed_mode: AlreadySignedMode = ALREADY_SIGNED_MODE_DEFAULT
    """
    How to handle already signed transaction. "strict" will just trigger a warning during autosign (will be skipped).
    """
    force_unsign: bool = False
    chain_id: str | None = None
    save_file_path: Path | None = None
    force_save_format: Literal["json", "bin"] | None = None
    serialization_mode: Literal["legacy", "hf26"] | None = None
    broadcast: bool = False

    async def _execute(self) -> None:
        transaction = await BuildTransaction(content=self.content, node=self.node).execute_with_result()

        # First, unsign if requested (removes existing signatures)
        if self.force_unsign:
            transaction = await UnSign(transaction=transaction).execute_with_result()

        # Then, sign with new signatures if requested
        if self.sign_key or self.sign_keys or self.autosign:
            assert self.unlocked_wallet is not None, (
                "wallet is required when sign_key/sign_keys or autosign is provided"
            )

            # Validate that only one signing method is used
            signing_methods = [self.sign_key is not None, self.sign_keys is not None, self.autosign]
            assert sum(signing_methods) == 1, "only one of sign_key, sign_keys, or autosign can be provided"

            if self.autosign:
                try:
                    transaction = await AutoSign(
                        unlocked_wallet=self.unlocked_wallet,
                        transaction=transaction,
                        keys=self.app_state.world.profile.keys,
                        chain_id=self.chain_id or await self.node.chain_id,
                        already_signed_mode=self.already_signed_mode,
                    ).execute_with_result()
                except TransactionAlreadySignedAutoSignError:
                    # We don't want to raise an error if the transaction is already signed, just skip the signing step.
                    warnings.warn(AutoSignSkippedWarning(), stacklevel=1)
            elif self.sign_key:
                transaction = await Sign(
                    unlocked_wallet=self.unlocked_wallet,
                    transaction=transaction,
                    key=self.sign_key,
                    chain_id=self.chain_id or await self.node.chain_id,
                    already_signed_mode=self.already_signed_mode,
                ).execute_with_result()
            elif self.sign_keys:
                # Sign with multiple keys in order, using multisign mode
                for key in self.sign_keys:
                    transaction = await Sign(
                        unlocked_wallet=self.unlocked_wallet,
                        transaction=transaction,
                        key=key,
                        chain_id=self.chain_id or await self.node.chain_id,
                        already_signed_mode="multisign",
                    ).execute_with_result()

        if path := self.save_file_path:
            await SaveTransaction(
                transaction=transaction,
                file_path=path,
                force_format=self.force_save_format,
                serialization_mode=self.serialization_mode,
            ).execute()

        if self.broadcast:
            await Broadcast(node=self.node, transaction=transaction).execute()

        self._result = transaction
