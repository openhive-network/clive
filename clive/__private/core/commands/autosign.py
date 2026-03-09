from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from clive.__private.core.commands.abc.command import Command, CommandError
from clive.__private.core.commands.abc.command_in_unlocked import CommandInUnlocked
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.commands.prefetch_transaction_authorities import PrefetchTransactionAuthorities
from clive.__private.core.constants.data_retrieval import ALREADY_SIGNED_MODE_DEFAULT
from clive.__private.core.iwax import (
    calculate_sig_digest,
    collect_signing_keys,
    convert_schemas_account_to_python_authorities,
    minimize_required_signatures,
)
from clive.__private.core.keys.key_manager import KeyManager, KeyNotFoundError, MultipleKeysFoundError
from clive.__private.logger import logger
from clive.__private.models.transaction import Transaction
from clive.__private.settings import safe_settings

if TYPE_CHECKING:
    import wax
    from clive.__private.core.node import Node
    from clive.__private.core.types import AlreadySignedMode
    from clive.__private.models.schemas import Signature


class AutoSignCommandError(CommandError):
    """Base error for all autosign related errors."""


class TooManyKeysAutoSignError(AutoSignCommandError):
    REASON: Final[str] = "Autosign cannot be used when there are multiple keys available."

    def __init__(self, command: Command) -> None:
        super().__init__(command, self.REASON)


class NoKeyAutoSignError(AutoSignCommandError):
    REASON: Final[str] = "Autosign cannot be used when there is no key available."

    def __init__(self, command: Command) -> None:
        super().__init__(command, self.REASON)


class AuthorityPrefetchAutoSignError(AutoSignCommandError):
    REASON: Final[str] = "Autosign failed: could not fetch required authorities from the node."

    def __init__(self, command: Command, cause: Exception) -> None:
        self.cause = cause
        super().__init__(command, self.REASON)


class TransactionAlreadySignedAutoSignError(AutoSignCommandError):
    REASON: Final[str] = "Your transaction is already signed."

    def __init__(self, command: Command) -> None:
        super().__init__(command, self.REASON)


@dataclass(kw_only=True)
class AutoSign(CommandInUnlocked, CommandWithResult[Transaction]):
    transaction: Transaction
    keys: KeyManager
    chain_id: str
    node: Node
    already_signed_mode: AlreadySignedMode = ALREADY_SIGNED_MODE_DEFAULT
    """How to handle the situation when transaction is already signed."""

    async def _execute(self) -> None:
        self._throw_wrong_already_signed_mode()
        self._throw_is_transaction_already_signed()

        if self.already_signed_mode == "override":
            self.transaction.signatures = []  # clear before signing

        # remove this condition when wax autosign is fully rolled out and tested
        if safe_settings.use_wax_autosign:
            await self._sign_with_wax_autosign()
        else:
            await self._sign_with_single_key()

        self._result = self.transaction

    async def _sign_with_single_key(self) -> None:
        try:
            key = self.keys.unique_key
        except KeyNotFoundError:
            raise NoKeyAutoSignError(self) from None
        except MultipleKeysFoundError:
            raise TooManyKeysAutoSignError(self) from None

        sig_digest = calculate_sig_digest(self.transaction, self.chain_id)
        result = await self.unlocked_wallet.sign_digest(sig_digest=sig_digest, key=key.value)
        self._set_transaction_signature(result)

    async def _sign_with_wax_autosign(self) -> None:
        try:
            cache = await PrefetchTransactionAuthorities(
                transaction=self.transaction, node=self.node
            ).execute_with_result()
        except Exception as error:
            raise AuthorityPrefetchAutoSignError(self, error) from error

        authorities_map: dict[str, wax.python_authorities] = {
            name: convert_schemas_account_to_python_authorities(account) for name, account in cache.items()
        }

        def retrieve_authorities(account_names: list[str]) -> dict[str, wax.python_authorities]:
            return {name: authorities_map[name] for name in account_names if name in authorities_map}

        approving_keys = collect_signing_keys(self.transaction, retrieve_authorities)
        logger.debug(f"AutoSign: approving keys: {approving_keys}")

        profile_public_keys = [key.value for key in self.keys]
        matching_keys = [key for key in approving_keys if key in profile_public_keys]
        logger.debug(f"AutoSign: matching keys in profile: {matching_keys}")

        # Save existing signatures before any changes — they are always preserved in the final result
        # (for override mode the caller is expected to clear signatures before invoking AutoSign)
        existing_signatures = list(self.transaction.signatures)

        # Minimize FIRST (as wallet.cpp does).
        # In "multisign" mode the transaction already holds signatures from other parties;
        # minimize_required_signatures considers them (by recovering public keys from the sigs)
        # and returns only the subset of matching_keys that is still needed.
        minimal_keys = minimize_required_signatures(
            self.transaction,
            self.chain_id,
            matching_keys,
            authorities_map,
            lambda _witness: "",
        )
        logger.debug(f"AutoSign: minimal keys after minimization: {minimal_keys}")

        # Sign only with the minimal set
        sig_digest = calculate_sig_digest(self.transaction, self.chain_id)
        existing_sig_set = set(existing_signatures)
        new_signatures = []
        for key in minimal_keys:
            signature = await self.unlocked_wallet.sign_digest(sig_digest=sig_digest, key=key)
            # Hive signing is deterministic (RFC 6979): skip if already present (multisign dedup)
            if signature not in existing_sig_set:
                new_signatures.append(signature)

        # Existing signatures are always preserved
        self.transaction.signatures = existing_signatures + new_signatures

    def _throw_wrong_already_signed_mode(self) -> None:
        if self.already_signed_mode not in ["strict", "multisign", "override"]:
            raise NotImplementedError(f"Unknown already_signed_mode: {self.already_signed_mode}")

    def _throw_is_transaction_already_signed(self) -> None:
        if self.already_signed_mode == "strict" and self.transaction.is_signed:
            raise TransactionAlreadySignedAutoSignError(self)

    def _set_transaction_signature(self, signature: Signature) -> None:
        self.transaction.signatures = [signature]
