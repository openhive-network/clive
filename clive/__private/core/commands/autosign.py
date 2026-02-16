from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from clive.__private.core.commands.abc.command import Command, CommandError
from clive.__private.core.commands.abc.command_in_unlocked import CommandInUnlocked
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.constants.data_retrieval import ALREADY_SIGNED_MODE_DEFAULT
from clive.__private.core.iwax import (
    calculate_sig_digest,
    minimize_required_signatures,
)
from clive.__private.models.transaction import Transaction

if TYPE_CHECKING:
    from collections.abc import Iterable

    import wax
    from clive.__private.core.accounts.accounts import TrackedAccount
    from clive.__private.core.node import Node
    from clive.__private.core.types import AlreadySignedMode


class AutoSignCommandError(CommandError):
    """Base error for all autosign related errors."""


class WrongAlreadySignedModeAutoSignError(AutoSignCommandError):
    def __init__(self, command: Command, already_signed_mode: AlreadySignedMode) -> None:
        self.already_signed_mode: AlreadySignedMode = already_signed_mode
        self.reason = f"Autosign cannot be used together with already_signed_mode {self.already_signed_mode}. "
        super().__init__(command, self.reason)


class NoMatchingKeyAutoSignError(AutoSignCommandError):
    REASON: Final[str] = "None of the keys in the wallet match the keys required to sign this transaction."

    def __init__(self, command: Command) -> None:
        super().__init__(command, self.REASON)


class InsufficientAuthorityDataError(AutoSignCommandError):
    def __init__(self, command: Command, missing_accounts: list[str]) -> None:
        self.missing_accounts = missing_accounts
        accounts_str = ", ".join(missing_accounts)
        self.reason = (
            f"Cannot determine signing keys. Authority data is missing for: {accounts_str}. "
            "These accounts may not exist on the blockchain."
        )
        super().__init__(command, self.reason)


class TransactionAlreadySignedAutoSignError(AutoSignCommandError):
    REASON: Final[str] = "Your transaction is already signed."

    def __init__(self, command: Command) -> None:
        super().__init__(command, self.REASON)


@dataclass(kw_only=True)
class AutoSign(CommandInUnlocked, CommandWithResult[Transaction]):
    transaction: Transaction
    node: Node
    tracked_accounts: Iterable[TrackedAccount]
    chain_id: str
    already_signed_mode: AlreadySignedMode = ALREADY_SIGNED_MODE_DEFAULT
    """How to handle the situation when transaction is already signed."""

    async def _execute(self) -> None:
        from clive.__private.core.commands.prefetch_transaction_authorities import (  # noqa: PLC0415
            PrefetchTransactionAuthorities,
        )
        from clive.__private.core.iwax import collect_signing_keys  # noqa: PLC0415

        self._throw_wrong_already_signed_mode()
        self._throw_is_transaction_already_signed()

        authorities_cache = await PrefetchTransactionAuthorities(
            transaction=self.transaction,
            node=self.node,
            tracked_accounts=self.tracked_accounts,
        ).execute_with_result()

        def _retrieve_from_cache(account_names: list[str]) -> dict[str, wax.python_authorities]:
            return {name: authorities_cache[name] for name in account_names if name in authorities_cache}

        required_keys = collect_signing_keys(self.transaction, _retrieve_from_cache)

        wallet_keys = await self.unlocked_wallet.public_keys
        wallet_key_set = {str(key) for key in wallet_keys}
        matching_keys = [key for key in required_keys if key in wallet_key_set]

        if not matching_keys:
            raise NoMatchingKeyAutoSignError(self)

        sig_digest = calculate_sig_digest(self.transaction, self.chain_id)
        for key in matching_keys:
            signature = await self.unlocked_wallet.sign_digest(sig_digest=sig_digest, key=key)
            self.transaction.signatures.append(signature)

        minimal_keys = minimize_required_signatures(
            self.transaction,
            self.chain_id,
            matching_keys,
            authorities_cache,
            self._get_witness_key_stub,
        )

        if len(minimal_keys) < len(matching_keys):
            self.transaction.signatures = []
            for key in minimal_keys:
                signature = await self.unlocked_wallet.sign_digest(sig_digest=sig_digest, key=key)
                self.transaction.signatures.append(signature)

        self._result = self.transaction

    @staticmethod
    def _get_witness_key_stub(_witness_name: str) -> str:
        return ""

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
