from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from clive.__private.core.commands.abc.command import Command, CommandError
from clive.__private.core.commands.abc.command_in_unlocked import CommandInUnlocked
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.constants.data_retrieval import ALREADY_SIGNED_MODE_DEFAULT
from clive.__private.core.iwax import calculate_sig_digest
from clive.__private.core.keys.key_manager import KeyManager, KeyNotFoundError, MultipleKeysFoundError
from clive.__private.models import Transaction

if TYPE_CHECKING:
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


class TransactionAlreadySignedAutoSignError(AutoSignCommandError):
    REASON: Final[str] = "Your transaction is already signed."

    def __init__(self, command: Command) -> None:
        super().__init__(command, self.REASON)


@dataclass(kw_only=True)
class AutoSign(CommandInUnlocked, CommandWithResult[Transaction]):
    transaction: Transaction
    keys: KeyManager
    chain_id: str
    already_signed_mode: AlreadySignedMode = ALREADY_SIGNED_MODE_DEFAULT
    """How to handle the situation when transaction is already signed."""

    async def _execute(self) -> None:
        self._throw_wrong_already_signed_mode()
        self._throw_is_transaction_already_signed()
        self._throw_no_unique_key()

        sig_digest = calculate_sig_digest(self.transaction, self.chain_id)
        result = await self.unlocked_wallet.sign_digest(sig_digest=sig_digest, key=self.keys.unique_key.value)
        self._set_transaction_signature(result)
        self._result = self.transaction

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

    def _throw_no_unique_key(self) -> None:
        try:
            _ = self.keys.unique_key
        except KeyNotFoundError:
            raise NoKeyAutoSignError(self) from None
        except MultipleKeysFoundError:
            raise TooManyKeysAutoSignError(self) from None

    def _set_transaction_signature(self, signature: Signature) -> None:
        self.transaction.signatures = [signature]
