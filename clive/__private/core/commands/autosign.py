from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from clive.__private.core.commands.abc.command import Command, CommandError
from clive.__private.core.commands.abc.command_in_unlocked import CommandInUnlocked
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.constants.data_retrieval import ALREADY_SIGNED_MODE_DEFAULT
from clive.__private.core.iwax import calculate_sig_digest
from clive.__private.core.keys import MultipleKeysFoundError, NoUniqueKeyFoundError
from clive.__private.models import Transaction

if TYPE_CHECKING:
    from clive.__private.core.profile import Profile
    from clive.__private.core.types import AlreadySignedMode
    from clive.__private.models.schemas import Signature


class AutoSignCommandError(CommandError):
    pass


class TransactionAutoSignWrongSignedModeError(AutoSignCommandError):
    def __init__(self, command: Command, already_signed_mode: AlreadySignedMode) -> None:
        reason = (
            f"Autosign cannot be used together with already_signed_mode {already_signed_mode}. "
            f"Please use already_signed_mode 'error' or do not specify it at all."
        )
        super().__init__(command, reason)


class TransactionAutoSignTooManyKeysError(AutoSignCommandError):
    REASON: Final[str] = (
        "Autosign cannot be used when there are multiple keys assigned to the profile."
        " Please use --sign-with to specify the key to sign the transaction."
    )

    def __init__(self, command: Command) -> None:
        super().__init__(command, self.REASON)


class TransactionAutoSignNoKeysError(AutoSignCommandError):
    REASON: Final[str] = "No keys are available in the profile. Cannot autosign the transaction."

    def __init__(self, command: Command) -> None:
        super().__init__(command, self.REASON)


@dataclass(kw_only=True)
class AutoSign(CommandInUnlocked, CommandWithResult[Transaction]):
    transaction: Transaction
    profile: Profile
    chain_id: str
    already_signed_mode: AlreadySignedMode = ALREADY_SIGNED_MODE_DEFAULT
    """How to handle the situation when transaction is already signed."""

    async def _execute(self) -> None:
        self._throw_wrong_already_signed_mode()
        if self._is_already_signed():
            self._result = self.transaction
        else:
            self._throw_no_default_key()
            sig_digest = calculate_sig_digest(self.transaction, self.chain_id)
            result = await self.unlocked_wallet.sign_digest(
                sig_digest=sig_digest, key=self.profile.keys.single_key.value
            )
            self._set_transaction_signature(result)
            self._result = self.transaction

    def _throw_wrong_already_signed_mode(self) -> None:
        if self.already_signed_mode == "error":
            pass
        elif self.already_signed_mode in ["multisign", "override"]:
            raise TransactionAutoSignWrongSignedModeError(self, self.already_signed_mode)
        else:
            raise NotImplementedError(f"Unknown already_signed_mode: {self.already_signed_mode}")

    def _throw_no_default_key(self) -> None:
        try:
            _ = self.profile.keys.single_key
        except NoUniqueKeyFoundError:
            raise TransactionAutoSignTooManyKeysError(self) from None
        except MultipleKeysFoundError:
            raise TransactionAutoSignTooManyKeysError(self) from None

    def _is_already_signed(self) -> bool:
        if self.transaction.is_signed:
            from clive.__private.cli.notify import print_warning  # noqa: PLC0415
            from clive.__private.cli.warnings import typer_echo_warnings  # noqa: PLC0415

            message = (
                "Your transaction is already signed. Autosign was skipped. If you want to multisign your "
                "transaction, use --already-signed-mode multisign. "
                "For more information, check clive process transaction -h"
            )
            with typer_echo_warnings():
                print_warning(message)
            return True
        return False

    def _set_transaction_signature(self, signature: Signature) -> None:
        self.transaction.signatures = [signature]
