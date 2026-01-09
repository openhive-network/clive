from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.core.commands.encrypt_memo import EncryptMemoKeyNotImportedError
from clive.__private.core.commands.encrypt_memo_with_account_names import AccountNotFoundForEncryptionError
from clive.__private.models.schemas import TransferOperation

if TYPE_CHECKING:
    from clive.__private.cli.types import ComposeTransaction
    from clive.__private.models.asset import Asset


class CLIEncryptMemoKeyNotImportedError(CLIPrettyError):
    def __init__(self) -> None:
        super().__init__("Failed to encrypt memo. You might not have the required memo key in your wallet.")


class CLIAccountNotFoundForEncryptionError(CLIPrettyError):
    def __init__(self, account_name: str) -> None:
        super().__init__(f"Cannot encrypt memo: account '{account_name}' was not found on the blockchain.")


@dataclass(kw_only=True)
class Transfer(OperationCommand):
    from_account: str
    to: str
    amount: Asset.LiquidT
    memo: str

    async def _create_operations(self) -> ComposeTransaction:
        memo = await self._maybe_encrypt_memo()
        yield TransferOperation(
            from_=self.from_account,
            to=self.to,
            amount=self.amount,
            memo=memo,
        )

    async def _maybe_encrypt_memo(self) -> str:
        """
        Encrypt the memo if it starts with '#'.

        Returns:
            The encrypted memo if it starts with '#', otherwise the original memo.

        Raises:
            CLIEncryptMemoKeyNotImportedError: If encryption fails because memo key is not imported.
            CLIAccountNotFoundForEncryptionError: If sender or receiver account doesn't exist.
        """
        if not self.memo.startswith("#"):
            return self.memo

        try:
            # Encrypt the memo using account names
            encrypted = await self.world.commands.encrypt_memo_with_account_names(
                content=self.memo,
                from_account=self.from_account,
                to_account=self.to,
            )
        except EncryptMemoKeyNotImportedError as error:
            raise CLIEncryptMemoKeyNotImportedError from error
        except AccountNotFoundForEncryptionError as error:
            raise CLIAccountNotFoundForEncryptionError(error.account_name) from error
        else:
            return encrypted.result_or_raise
