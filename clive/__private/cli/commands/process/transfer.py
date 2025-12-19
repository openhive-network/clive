from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.core.commands.encrypt_memo import CommandEncryptMemoError
from clive.__private.models.schemas import TransferOperation

if TYPE_CHECKING:
    from clive.__private.cli.types import ComposeTransaction
    from clive.__private.models.asset import Asset


class EncryptMemoError(CLIPrettyError):
    def __init__(self) -> None:
        super().__init__("Failed to encrypt memo. You might not have the correct memo key in your wallet.")


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
            CLIPrettyError: If the from_account or to_account is not found on the blockchain,
                or if encryption fails due to beekeeper errors (e.g., memo key not stored).
        """
        if not self.memo.startswith("#"):
            return self.memo

        try:
            # Encrypt the memo using account names
            encrypted = await self.world.commands.encrypt_memo_from_accounts(
                content=self.memo,
                from_account=self.from_account,
                to_account=self.to,
            )
        except CommandEncryptMemoError as e:
            # Handle beekeeper errors (e.g., memo key not stored in beekeeper)
            raise EncryptMemoError from e
        else:
            return encrypted.result_or_raise
