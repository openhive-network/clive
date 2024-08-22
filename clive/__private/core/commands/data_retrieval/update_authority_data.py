from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from clive.__private.core.authority import AllAuthorities, Authority
from clive.__private.core.commands.abc.command_data_retrieval import CommandDataRetrieval

if TYPE_CHECKING:
    from clive.__private.core.accounts.accounts import TrackedAccount
    from clive.__private.core.node import Node
    from clive.__private.core.types import AuthorityType
    from clive.models.aliased import FindAccounts


class InvalidAuthorityError(Exception):
    pass


@dataclass(kw_only=True)
class UpdateAuthorityData(CommandDataRetrieval[AllAuthorities, AllAuthorities, AllAuthorities]):
    node: Node
    account: TrackedAccount
    _max_sig_check_depth: int = field(init=False)

    async def _execute(self) -> None:
        await super()._execute()

    async def _harvest_data_from_api(self) -> AllAuthorities:
        config = await self.node.cached.config
        self._max_sig_check_depth = config.HIVE_MAX_SIG_CHECK_DEPTH
        find_accounts_data = await self.node.api.database_api.find_accounts(accounts=[self.account.name])
        self._assert_account_names_matches_in_result([self.account.name], find_accounts_data)

        owner_lut = await self._create_lut(find_accounts_data, "owner")
        active_lut = await self._create_lut(find_accounts_data, "active")
        posting_lut = await self._create_lut(find_accounts_data, "posting")

        return AllAuthorities(
            name=find_accounts_data.accounts[0].name,
            owner=Authority.from_schemas_authority(find_accounts_data.accounts[0].owner),
            active=Authority.from_schemas_authority(find_accounts_data.accounts[0].active),
            posting=Authority.from_schemas_authority(find_accounts_data.accounts[0].posting),
            owner_lut=owner_lut,
            active_lut=active_lut,
            posting_lut=posting_lut,
            last_updated=datetime.now(timezone.utc),
        )

    def get_next_level_authorities(
        self, find_accounts_data: FindAccounts, authority_type: AuthorityType
    ) -> dict[str, Authority]:
        match authority_type:
            case "owner":
                return {
                    account.name: Authority.from_schemas_authority(account.owner)
                    for account in find_accounts_data.accounts
                }
            case "active":
                return {
                    account.name: Authority.from_schemas_authority(account.active)
                    for account in find_accounts_data.accounts
                }
            case "posting":
                return {
                    account.name: Authority.from_schemas_authority(account.posting)
                    for account in find_accounts_data.accounts
                }
            case _:
                raise InvalidAuthorityError

    async def _create_lut(
        self, find_accounts_data: FindAccounts, authority_type: AuthorityType
    ) -> dict[str, Authority]:
        next_level_authorities = self.get_next_level_authorities(find_accounts_data, authority_type)
        lut = next_level_authorities.copy()
        for _ in range(self._max_sig_check_depth):
            next_level_account_names: list[str] = [
                account_weight_tuple[0]
                for auth in list(next_level_authorities.values())
                for account_weight_tuple in auth.account_auths
            ]
            if len(next_level_account_names) == 0:
                break
            find_accounts_data = await self.node.api.database_api.find_accounts(accounts=next_level_account_names)
            self._assert_account_names_matches_in_result(next_level_account_names, find_accounts_data)
            next_level_authorities = self.get_next_level_authorities(find_accounts_data, authority_type)
            lut.update(next_level_authorities)
        return lut

    def _assert_account_names_matches_in_result(self, expected_account_names: list[str], result: FindAccounts) -> None:
        accounts = result.accounts
        assert len(expected_account_names) == len(accounts), "Not all accounts were found when fetching authority data"
        assert all(
            account.name in expected_account_names for account in accounts
        ), "Account list mismatch when fetching authority data"

    async def _process_data(self, authorities: AllAuthorities) -> AllAuthorities:
        self.account._authorities = authorities
        return authorities
