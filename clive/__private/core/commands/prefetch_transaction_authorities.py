from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import wax
from clive.__private.core._async import asyncio_run
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.iwax import (
    collect_signing_keys,
    convert_schemas_account_to_python_authorities,
    convert_wax_authorities_to_python_authorities,
)

if TYPE_CHECKING:
    from collections.abc import Iterable

    from clive.__private.core.accounts.accounts import TrackedAccount
    from clive.__private.core.node import Node
    from clive.__private.models.transaction import Transaction


@dataclass(kw_only=True)
class PrefetchTransactionAuthorities(CommandWithResult[dict[str, wax.python_authorities]]):
    """Pre-fetches authority data for all accounts needed by a transaction, including account_auths chains."""

    transaction: Transaction
    node: Node
    tracked_accounts: Iterable[TrackedAccount]
    _authorities_cache: dict[str, wax.python_authorities] = field(default_factory=dict, init=False)

    async def _execute(self) -> None:
        self._build_authorities_from_tracked_accounts()
        collect_signing_keys(self.transaction, self._retrieve_and_fetch_authorities)
        self._result = self._authorities_cache

    def _build_authorities_from_tracked_accounts(self) -> None:
        for account in self.tracked_accounts:
            if account.is_node_data_available:
                self._authorities_cache[account.name] = convert_wax_authorities_to_python_authorities(
                    account.data.authority.wax_authorities
                )

    def _retrieve_and_fetch_authorities(self, account_names: list[str]) -> dict[str, wax.python_authorities]:
        result: dict[str, wax.python_authorities] = {}
        missing: list[str] = []

        for name in account_names:
            if name in self._authorities_cache:
                result[name] = self._authorities_cache[name]
            else:
                missing.append(name)

        if missing:
            fetched_accounts = asyncio_run(self.node.api.database_api.find_accounts(accounts=missing))
            for account in fetched_accounts.accounts:
                authorities = convert_schemas_account_to_python_authorities(account)
                self._authorities_cache[account.name] = authorities
                result[account.name] = authorities

        return result
