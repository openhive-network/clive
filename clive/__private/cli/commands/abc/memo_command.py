from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import cast

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.exceptions import CLIPrettyError, CLIPrivateKeyInMemoValidationError
from clive.__private.core.commands.encrypt_memo import EncryptMemoKeyNotImportedError
from clive.__private.core.commands.encrypt_memo_with_account_names import AccountNotFoundForEncryptionError
from clive.__private.core.formatters.humanize import humanize_validation_result
from clive.__private.validators.private_key_in_memo_validator import PrivateKeyInMemoValidator


class CLIEncryptMemoKeyNotImportedError(CLIPrettyError):
    def __init__(self) -> None:
        super().__init__("Failed to encrypt memo. You might not have the required memo key in your wallet.")


class CLIAccountNotFoundForEncryptionError(CLIPrettyError):
    def __init__(self, account_name: str) -> None:
        super().__init__(f"Cannot encrypt memo: account '{account_name}' was not found on the blockchain.")


@dataclass(kw_only=True)
class MemoCommand(WorldBasedCommand, ABC):
    memo: str | None

    @property
    def ensure_memo(self) -> str:
        memo = self.memo
        assert self.is_option_given(memo)
        return cast("str", memo)

    async def fetch_data(self) -> None:
        await super().fetch_data()
        await self.world.commands.update_node_data(accounts=self.profile.accounts.tracked)

    async def validate_inside_context_manager(self) -> None:
        self._validate_private_key_in_memo(self.ensure_memo)
        await super().validate_inside_context_manager()

    async def _maybe_encrypt_memo(
        self, memo_plaintext: str, sender_account_name: str, receiver_account_name: str
    ) -> str:
        """
        Encrypt the memo if it starts with '#'.

        Args:
            memo_plaintext: The memo text to potentially encrypt.
            sender_account_name: Account name of the sender.
            receiver_account_name: Account name of the receiver.

        Returns:
            The encrypted memo if it starts with '#', otherwise the original memo.

        Raises:
            CLIEncryptMemoKeyNotImportedError: If encryption fails because memo key is not imported.
            CLIAccountNotFoundForEncryptionError: If sender or receiver account doesn't exist.
        """
        if not memo_plaintext.startswith("#"):
            return memo_plaintext

        try:
            encrypted = await self.world.commands.encrypt_memo_with_account_names(
                content=memo_plaintext,
                from_account=sender_account_name,
                to_account=receiver_account_name,
            )
        except EncryptMemoKeyNotImportedError as error:
            raise CLIEncryptMemoKeyNotImportedError from error
        except AccountNotFoundForEncryptionError as error:
            raise CLIAccountNotFoundForEncryptionError(error.account_name) from error
        else:
            return encrypted.result_or_raise

    def _validate_private_key_in_memo(self, memo_value: str) -> None:
        memo_validator = PrivateKeyInMemoValidator(self.world)
        result = memo_validator.validate(value=memo_value)
        if not result.is_valid:
            raise CLIPrivateKeyInMemoValidationError(humanize_validation_result(result))
