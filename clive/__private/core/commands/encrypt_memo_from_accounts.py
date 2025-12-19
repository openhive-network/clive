from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_in_unlocked import CommandInUnlocked
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.commands.encrypt_memo import EncryptMemo
from clive.__private.core.keys import PublicKey

if TYPE_CHECKING:
    from clive.__private.core.node.node import Node


@dataclass(kw_only=True)
class EncryptMemoFromAccounts(CommandInUnlocked, CommandWithResult[str]):
    """
    Encrypt a memo by looking up accounts and using their memo keys.

    Attributes:
        content: The memo content to encrypt.
        from_account: The sender's account name.
        to_account: The recipient's account name.
        node: The node to use for account lookup.
    """

    content: str
    from_account: str
    to_account: str
    node: Node

    async def _execute(self) -> None:
        # Find accounts on the blockchain
        from clive.__private.core.commands.find_accounts import FindAccounts  # noqa: PLC0415

        find_accounts_command = FindAccounts(
            node=self.node,
            accounts=[self.from_account, self.to_account],
        )
        accounts = await find_accounts_command.execute_with_result()

        # Extract memo keys (FindAccounts ensures both accounts exist)
        from_account_data = next(acc for acc in accounts if acc.name == self.from_account)
        to_account_data = next(acc for acc in accounts if acc.name == self.to_account)

        from_memo_key = PublicKey.create(from_account_data.memo_key)
        to_memo_key = PublicKey.create(to_account_data.memo_key)

        # Encrypt using the memo keys
        encrypt_command = EncryptMemo(
            unlocked_wallet=self.unlocked_wallet,
            content=self.content,
            from_key=from_memo_key,
            to_key=to_memo_key,
        )
        self._result = await encrypt_command.execute_with_result()
