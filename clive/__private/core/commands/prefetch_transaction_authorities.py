from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.commands.find_accounts import AccountNotFoundError, FindAccounts
from clive.__private.core.constants.authority import HIVE_MAX_SIG_CHECK_DEPTH
from clive.__private.core.iwax import get_transaction_required_authorities
from clive.__private.logger import logger
from clive.__private.models.schemas import Account

if TYPE_CHECKING:
    from clive.__private.core.node import Node
    from clive.__private.models.transaction import Transaction

type AccountAuthorities = dict[str, Account]


@dataclass(kw_only=True)
class PrefetchTransactionAuthorities(CommandWithResult[AccountAuthorities]):
    """
    Prefetches account authority data needed for transaction signing.

    Starts from accounts required to authorize the transaction (active/owner/posting),
    then fetches in breadth-first, batched layers up to HIVE_MAX_SIG_CHECK_DEPTH,
    following account_auths references at each level.

    Attributes:
        transaction: The transaction to analyze for required signing authorities.
        node: The node to fetch account data from.
    """

    transaction: Transaction
    node: Node
    _cache: dict[str, Account] = field(default_factory=dict, init=False)

    async def _execute(self) -> None:
        required = get_transaction_required_authorities(self.transaction)
        initial_accounts = list(required.active_accounts | required.owner_accounts | required.posting_accounts)
        for other_auth in required.other_authorities:
            for account_name in other_auth.account_auths:
                if account_name not in initial_accounts:
                    initial_accounts.append(account_name)

        await self._fetch_and_cache(initial_accounts)

        previous_layer = initial_accounts
        for _depth in range(1, HIVE_MAX_SIG_CHECK_DEPTH + 1):
            new_accounts = self._collect_account_auths_from_cached(previous_layer)
            if not new_accounts:
                break
            await self._fetch_and_cache(new_accounts)
            previous_layer = new_accounts

        self._result = self._cache

    async def _fetch_and_cache(self, account_names: list[str]) -> None:
        names_to_fetch = [name for name in account_names if name not in self._cache]
        if not names_to_fetch:
            return

        try:
            accounts = await FindAccounts(node=self.node, accounts=names_to_fetch).execute_with_result()
        except AccountNotFoundError:
            logger.debug(f"Some accounts not found during authority prefetch: {names_to_fetch}, fetching individually.")
            accounts = await self._fetch_accounts_individually(names_to_fetch)

        for account in accounts:
            self._cache[account.name] = account

    async def _fetch_accounts_individually(self, account_names: list[str]) -> list[Account]:
        results: list[Account] = []
        for name in account_names:
            try:
                found = await FindAccounts(node=self.node, accounts=[name]).execute_with_result()
                results.extend(found)
            except AccountNotFoundError:
                logger.debug(f"Account '{name}' not found on node, skipping.")
        return results

    def _collect_account_auths_from_cached(self, previous_layer_names: list[str]) -> list[str]:
        new_names: list[str] = []
        for name in previous_layer_names:
            account = self._cache.get(name)
            if account is None:
                continue
            for authority in (account.owner, account.active, account.posting):
                for auth_account_name, _weight in authority.account_auths:
                    if auth_account_name not in self._cache and auth_account_name not in new_names:
                        new_names.append(auth_account_name)
        return new_names
