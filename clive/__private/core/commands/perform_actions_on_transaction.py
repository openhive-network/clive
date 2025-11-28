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
from clive.__private.core.constants.transaction import ALREADY_SIGNED_MODE_DEFAULT, DEFAULT_SERIALIZATION_MODE
from clive.__private.core.keys import PublicKey
from clive.__private.models.transaction import Transaction

if TYPE_CHECKING:
    from beekeepy import AsyncUnlockedWallet

    from clive.__private.core.app_state import AppState
    from clive.__private.core.types import SerializationMode


if TYPE_CHECKING:
    from pathlib import Path

    from clive.__private.core.ensure_transaction import TransactionConvertibleType
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
        sign_keys: Single key or list of keys to sign the transaction with.
            If a list with multiple keys, uses multisign mode. Cannot be used with autosign.
        autosign: Whether to automatically sign the transaction.
        already_signed_mode: How to handle already signed transactions.
        force_unsign: Whether to remove the signature from the transaction. Even when sign_keys is provided.
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
    """Required if transaction needs to be signed - when sign_keys is provided."""
    sign_keys: PublicKey | list[PublicKey] | None = None
    autosign: bool = False
    already_signed_mode: AlreadySignedMode | None = None
    """
    How to handle already signed transaction.
    - If None (default): automatically determined based on context
      - "multisign" if multiple sign_keys are provided and transaction is not signed yet
      - "strict" (default) otherwise
    - If explicitly set: uses the provided mode regardless of context
    """
    force_unsign: bool = False
    chain_id: str | None = None
    save_file_path: Path | None = None
    force_save_format: Literal["json", "bin"] | None = None
    serialization_mode: SerializationMode = DEFAULT_SERIALIZATION_MODE
    broadcast: bool = False

    async def _execute(self) -> None:
        transaction = await BuildTransaction(content=self.content, node=self.node).execute_with_result()

        if not self.force_unsign and (self.sign_keys or self.autosign):
            assert self.unlocked_wallet is not None, "wallet is required when sign_keys or autosign is provided"
            assert not (self.sign_keys and self.autosign), "only one of sign_keys and autosign can be provided"

            if self.autosign:
                try:
                    transaction = await AutoSign(
                        unlocked_wallet=self.unlocked_wallet,
                        transaction=transaction,
                        keys=self.app_state.world.profile.keys,
                        chain_id=self.chain_id or await self.node.chain_id,
                        already_signed_mode=self.already_signed_mode or ALREADY_SIGNED_MODE_DEFAULT,
                    ).execute_with_result()
                except TransactionAlreadySignedAutoSignError:
                    # We don't want to raise an error if the transaction is already signed, just skip the signing step.
                    warnings.warn(AutoSignSkippedWarning(), stacklevel=1)
            elif self.sign_keys is not None:
                keys_to_sign = self._normalize_sign_keys(self.sign_keys)

                # Determine already_signed_mode - use dynamic evaluation if not explicitly provided
                already_signed_mode = self._determine_already_signed_mode(
                    keys_to_sign=keys_to_sign, transaction=transaction
                )

                for key in keys_to_sign:
                    transaction = await Sign(
                        unlocked_wallet=self.unlocked_wallet,
                        transaction=transaction,
                        key=key,
                        chain_id=self.chain_id or await self.node.chain_id,
                        already_signed_mode=already_signed_mode,
                    ).execute_with_result()

        if self.force_unsign:
            transaction = await UnSign(transaction=transaction).execute_with_result()

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

    def _determine_already_signed_mode(
        self, keys_to_sign: list[PublicKey], transaction: Transaction
    ) -> AlreadySignedMode:
        """
        Determine the already_signed_mode to use.

        If already_signed_mode is explicitly set, use that value.
        Otherwise, use dynamic evaluation:
        - "multisign" if multiple keys are given
        - default ("strict") otherwise

        Args:
            keys_to_sign: The list of keys to sign with.
            transaction: The transaction to check (currently not used in logic, but kept for future extensions).

        Returns:
            The determined already_signed_mode.
        """
        already_signed_mode = self.already_signed_mode

        if already_signed_mode is not None:
            # use the explicitly given value
            return already_signed_mode

        if len(keys_to_sign) > 1 and not transaction.is_signed:
            # if multiple keys are given and transaction is not signed yet, we can safely sign it
            return "multisign"

        # fallback to default
        return ALREADY_SIGNED_MODE_DEFAULT

    def _normalize_sign_keys(self, keys: PublicKey | list[PublicKey]) -> list[PublicKey]:
        """Normalize sign_keys to a list format."""
        return [keys] if isinstance(keys, PublicKey) else keys
