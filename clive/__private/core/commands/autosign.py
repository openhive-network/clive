from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from clive.__private.core.commands.abc.command import Command, CommandError
from clive.__private.core.commands.abc.command_in_unlocked import CommandInUnlocked
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.constants.data_retrieval import ALREADY_SIGNED_MODE_DEFAULT
from clive.__private.core.iwax import (
    calculate_sig_digest,
    collect_signing_keys,
    convert_schemas_account_to_python_authorities,
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


class WrongAlreadySignedModeAutoSignError(AutoSignCommandError):
    def __init__(self, command: Command, already_signed_mode: AlreadySignedMode) -> None:
        self.already_signed_mode: AlreadySignedMode = already_signed_mode
        self.reason = f"Autosign cannot be used together with already_signed_mode {self.already_signed_mode}. "
        super().__init__(command, self.reason)


class TooManyKeysAutoSignError(AutoSignCommandError):
    REASON: Final[str] = "Autosign cannot be used when there are multiple keys available."

    def __init__(self, command: Command) -> None:
        super().__init__(command, self.REASON)


class NoKeyAutoSignError(AutoSignCommandError):
    REASON: Final[str] = "Autosign cannot be used when there is no key available."

    def __init__(self, command: Command) -> None:
        super().__init__(command, self.REASON)


class NoMatchingKeyAutoSignError(AutoSignCommandError):
    REASON: Final[str] = "Autosign failed: wallet has keys but none match the transaction's required authorities."

    def __init__(self, command: Command) -> None:
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

        if self._has_single_unique_key():
            sig_digest = calculate_sig_digest(self.transaction, self.chain_id)
            result = await self.unlocked_wallet.sign_digest(sig_digest=sig_digest, key=self.keys.unique_key.value)
            self._set_transaction_signature(result)
        else:
            await self._sign_with_multiple_keys()

        self._result = self.transaction

    def _has_single_unique_key(self) -> bool:
        try:
            _ = self.keys.unique_key
        except KeyNotFoundError:
            raise NoKeyAutoSignError(self) from None
        except MultipleKeysFoundError:
            if not safe_settings.use_wax_autosign:
                raise TooManyKeysAutoSignError(self) from None
            return False
        return True

    async def _sign_with_multiple_keys(self) -> None:
        from clive.__private.core.commands.prefetch_transaction_authorities import (  # noqa: PLC0415
            PrefetchTransactionAuthorities,
        )

        cache = await PrefetchTransactionAuthorities(transaction=self.transaction, node=self.node).execute_with_result()

        authorities_map: dict[str, wax.python_authorities] = {
            name: convert_schemas_account_to_python_authorities(account) for name, account in cache.items()
        }

        def retrieve_authorities(account_names: list[str]) -> dict[str, wax.python_authorities]:
            return {name: authorities_map[name] for name in account_names if name in authorities_map}

        required_keys = collect_signing_keys(self.transaction, retrieve_authorities)
        logger.debug(f"AutoSign: required signing keys: {required_keys}")

        wallet_public_keys = [str(key) for key in await self.unlocked_wallet.public_keys]
        matching_keys = [key for key in required_keys if key in wallet_public_keys]
        logger.debug(f"AutoSign: matching keys in wallet: {matching_keys}")

        if not matching_keys:
            raise NoMatchingKeyAutoSignError(self)

        sig_digest = calculate_sig_digest(self.transaction, self.chain_id)
        signatures = []
        for key in matching_keys:
            signature = await self.unlocked_wallet.sign_digest(sig_digest=sig_digest, key=key)
            signatures.append(signature)
        self.transaction.signatures = signatures

    def _throw_wrong_already_signed_mode(self) -> None:
        if self.already_signed_mode == "strict":
            # autosign can be used only in `strict` mode
            return

        if self.already_signed_mode in ["multisign", "override"]:
            raise WrongAlreadySignedModeAutoSignError(self, self.already_signed_mode)

        raise NotImplementedError(f"Unknown already_signed_mode: {self.already_signed_mode}")

    def _throw_is_transaction_already_signed(self) -> None:
        if self.transaction.is_signed:
            raise TransactionAlreadySignedAutoSignError(self)

    def _set_transaction_signature(self, signature: Signature) -> None:
        self.transaction.signatures = [signature]
