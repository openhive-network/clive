from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from clive.__private.core.authority import AccountAuthority
from clive.__private.core.commands.abc.command_data_retrieval import CommandDataRetrieval
from clive.__private.core.types import AuthoritiesT

if TYPE_CHECKING:
    from clive.__private.core.accounts.accounts import TrackedAccount
    from clive.__private.core.node import Node
    from clive.__private.models.schemas import FindAccounts


class InvalidAuthorityError(Exception):
    pass


@dataclass(kw_only=True)
class UpdateAuthorityData(CommandDataRetrieval[AuthoritiesT, AuthoritiesT, AuthoritiesT]):
    node: Node
    account: TrackedAccount
    _depth: int = field(init=False)

    async def _execute(self) -> None:
        await super()._execute()

    async def _harvest_data_from_api(self) -> AuthoritiesT:
        self._depth = (await self.node.cached.config).HIVE_MAX_SIG_CHECK_DEPTH
        find_accounts_data = await self.node.api.database_api.find_accounts(accounts=[self.account.name])
        self._assert_account_names_matches_in_result([self.account.name], find_accounts_data)
        account_data = find_accounts_data.accounts[0]

        authorities = {
            AccountAuthority.from_schemas_authority(account_data.owner, account_data.name, "owner"),
            AccountAuthority.from_schemas_authority(account_data.active, account_data.name, "active"),
            AccountAuthority.from_schemas_authority(account_data.posting, account_data.name, "posting"),
        }
        authorities = await self.__fill_look_up_table(authorities)

        return authorities

    async def __fill_look_up_table(self, authorities: AuthoritiesT) -> AuthoritiesT:
        next_level_authorities: AuthoritiesT = authorities.copy()
        for _ in range(self._depth):
            next_level_account_names = {authority.account for authority in next_level_authorities}
            if len(next_level_account_names) == 0:
                break
            find_accounts_data = await self.node.api.database_api.find_accounts(accounts=next_level_account_names)
            self._assert_account_names_matches_in_result(next_level_account_names, find_accounts_data)
            next_level_authorities = self.__get_next_level_authorities(find_accounts_data)
            authorities.update(next_level_authorities)
        return authorities

    async def __get_next_level_authorities(self, result: FindAccounts) -> AuthoritiesT:
        next_level_authorities: AuthoritiesT = {}
        for account_data in result.accounts:
            next_level_authorities.update(
                {
                    AccountAuthority.from_schemas_authority(account_data.owner, account_data.name, "owner"),
                    AccountAuthority.from_schemas_authority(account_data.active, account_data.name, "active"),
                    AccountAuthority.from_schemas_authority(account_data.posting, account_data.name, "posting"),
                }
            )
        return next_level_authorities

    def _assert_account_names_matches_in_result(self, expected_account_names: list[str], result: FindAccounts) -> None:
        accounts = result.accounts
        assert len(expected_account_names) == len(accounts), "Not all accounts were found when fetching authority data"
        assert all(
            account.name in expected_account_names for account in accounts
        ), "Account list mismatch when fetching authority data"

    async def _process_data(self, authorities: AuthoritiesT) -> AuthoritiesT:
        self.account._authorities = {
            account_authority for account_authority in authorities if account_authority.name == self.account.name
        }
        self.account._authorities_lut = authorities
        return authorities
