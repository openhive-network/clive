from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import CommandError
from clive.__private.core.commands.abc.command_in_unlocked import CommandInUnlocked
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.constants.data_retrieval import ALREADY_SIGNED_MODE_DEFAULT
from clive.__private.core.iwax import calculate_sig_digest
from clive.__private.models import Transaction

if TYPE_CHECKING:
    from clive.__private.core.keys import PublicKey
    from clive.__private.core.types import AlreadySignedMode
    from clive.__private.models.schemas import Signature


class SignCommandError(CommandError):
    pass


class TransactionAlreadySignedError(SignCommandError):
    pass


@dataclass(kw_only=True)
class Sign(CommandInUnlocked, CommandWithResult[Transaction]):
    transaction: Transaction
    key: PublicKey
    chain_id: str
    already_signed_mode: AlreadySignedMode = ALREADY_SIGNED_MODE_DEFAULT
    """How to handle the situation when transaction is already signed."""

    async def _execute(self) -> None:
        self.__throw_already_signed_error_when_needed()

        sig_digest = calculate_sig_digest(self.transaction, self.chain_id)
        result = await self.unlocked_wallet.sign_digest(sig_digest=sig_digest, key=self.key.value)

        self.__set_transaction_signature(result)
        self._result = self.transaction

    def __throw_already_signed_error_when_needed(self) -> None:
        if self.already_signed_mode == "error" and self.transaction.is_signed:
            raise TransactionAlreadySignedError(self, "Transaction is already signed!")

    def __set_transaction_signature(self, signature: Signature) -> None:
        if self.already_signed_mode == "multisign":
            self.transaction.signatures.append(signature)
        elif self.already_signed_mode in ["override", "error"]:
            # this should be after the error check, because we don't want to take unnecessary action like signing
            # if we're going to throw an error anyway
            self.transaction.signatures = [signature]
        else:
            raise NotImplementedError(f"Unknown already_signed_mode: {self.already_signed_mode}")
