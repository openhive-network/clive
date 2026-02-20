from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from clive.__private.core import iwax
from clive.__private.core.cached_offline_data import CachedAuthority, CachedAuthorityRole, CachedNodeData, CachedTapos
from clive.__private.core.commands.abc.command import Command
from clive.__private.core.commands.find_accounts import FindAccounts
from clive.__private.core.date_utils import utc_now

if TYPE_CHECKING:
    from clive.__private.core.accounts.accounts import TrackedAccount
    from clive.__private.core.node import Node
    from clive.__private.core.profile import Profile


@dataclass(kw_only=True)
class FetchOfflineData(Command):
    node: Node
    profile: Profile
    accounts: list[TrackedAccount] = field(default_factory=list)

    async def _execute(self) -> None:
        gdpo = await self.node.api.database_api.get_dynamic_global_properties()
        tapos_data = iwax.get_tapos_data(gdpo.head_block_id)
        self.profile.cached_tapos = CachedTapos(
            ref_block_num=tapos_data.ref_block_num,
            ref_block_prefix=tapos_data.ref_block_prefix,
            head_block_time=gdpo.time,
        )

        # Cache chain_id so offline signing works without needing the node
        if not self.profile.chain_id:
            chain_id = await self.node.chain_id
            self.profile.set_chain_id(chain_id)

        if not self.accounts:
            return

        account_names = [acc.name for acc in self.accounts]
        accounts_data = await FindAccounts(node=self.node, accounts=account_names).execute_with_result()
        now = utc_now()
        for schema_account in accounts_data:
            tracked = next((a for a in self.accounts if a.name == schema_account.name), None)
            if tracked is None:
                continue
            tracked._cached_authority = CachedAuthority(
                owner=self._convert_authority_role(schema_account.owner),
                active=self._convert_authority_role(schema_account.active),
                posting=self._convert_authority_role(schema_account.posting),
                memo_key=str(schema_account.memo_key),
                fetch_time=now,
            )

        # Cache NodeData for accounts that have fresh data from update_node_data
        for account in self.accounts:
            if account.is_node_data_available:
                account._cached_node_data = CachedNodeData.from_node_data(account.data, now)

    @staticmethod
    def _convert_authority_role(authority: object) -> CachedAuthorityRole:
        return CachedAuthorityRole(
            key_auths=[(str(k), int(w)) for k, w in authority.key_auths],  # type: ignore[attr-defined]
            account_auths=[(str(a), int(w)) for a, w in authority.account_auths],  # type: ignore[attr-defined]
            weight_threshold=int(authority.weight_threshold),  # type: ignore[attr-defined]
        )
