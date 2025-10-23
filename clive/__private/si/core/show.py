from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.accounts.accounts import TrackedAccount
from clive.__private.core.commands.data_retrieval.witnesses_data import (
    WitnessData,
    WitnessesData,
    WitnessesDataRetrieval,
)
from clive.__private.core.profile import Profile
from clive.__private.si.core.base import CommandBase
from clive.__private.si.data_classes import Accounts, Authority, AuthorityInfo, Balances, Witness
from clive.__private.si.validators import AccountNameValidator, PageNumberValidator, PageSizeValidator

if TYPE_CHECKING:
    from clive.__private.core.types import AuthorityLevelRegular
    from clive.__private.core.world import World


class ShowProfiles(CommandBase[list[str]]):
    def __init__(self) -> None:
        pass

    async def _run(self) -> list[str]:
        return Profile.list_profiles()


class ShowBalances(CommandBase[Balances]):
    def __init__(self, world: World, account_name: str) -> None:
        self.world = world
        self.account_name = account_name

    def validate(self):
        AccountNameValidator().validate(self.account_name)

    async def _run(self) -> Balances:
        account = TrackedAccount(name=self.account_name)
        await self.world.commands.update_node_data(accounts=[account])

        return Balances(
            hbd_liquid=account.data.hbd_balance,
            hbd_savings=account.data.hbd_savings,
            hbd_unclaimed=account.data.hbd_unclaimed,
            hive_liquid=account.data.hive_balance,
            hive_savings=account.data.hive_savings,
            hive_unclaimed=account.data.hive_unclaimed,
        )


class ShowAccounts(CommandBase[Accounts]):
    def __init__(self, world: World) -> None:
        self.world = world

    async def _run(self) -> Accounts:
        profile = self.world.profile
        return Accounts(
            working_account=profile.accounts.working.name if profile.accounts.has_working_account else None,
            tracked_accounts=[account.name for account in profile.accounts.tracked],
            known_accounts=[account.name for account in profile.accounts.known],
        )


class ShowWitnesses(CommandBase[list[Witness]]):
    def __init__(self, world: World, account_name: str, page_size: int, page_no: int) -> None:
        self.world = world
        self.account_name = account_name
        self.page_size = page_size
        self.page_no = page_no

    def validate(self):
        AccountNameValidator().validate(self.account_name)
        PageSizeValidator().validate(self.page_size)
        PageNumberValidator().validate(self.page_no)

    async def _run(self) -> list[Witness]:
        witnesses_list_len, proxy, witnesses_chunk = await self.get_witness_chunk()
        return [
            Witness(
                voted=witness.voted,
                rank=witness.rank,
                witness_name=witness.name,
                votes=witness.votes,
                created=witness.created,
                missed_blocks=witness.missed_blocks,
                last_block=witness.last_block,
                price_feed=witness.price_feed,
                version=witness.version,
            )
            for witness in witnesses_chunk
        ]

    async def get_witness_chunk(self) -> tuple[int, str, list[WitnessData]]:
        accounts = (await self.world.commands.find_accounts(accounts=[self.account_name])).result_or_raise
        proxy = accounts[0].proxy

        wrapper = await self.world.commands.retrieve_witnesses_data(
            account_name=proxy if proxy else self.account_name,
            mode=WitnessesDataRetrieval.DEFAULT_MODE,
            witness_name_pattern=None,
            search_by_pattern_limit=WitnessesDataRetrieval.DEFAULT_SEARCH_BY_PATTERN_LIMIT,
        )
        witnesses_data: WitnessesData = wrapper.result_or_raise
        start_index: int = self.page_no * self.page_size
        end_index: int = start_index + self.page_size
        witnesses_list: list[WitnessData] = list(witnesses_data.witnesses.values())
        witnesses_chunk: list[WitnessData] = witnesses_list[start_index:end_index]

        return len(witnesses_list), proxy, witnesses_chunk


class ShowAuthority(CommandBase[AuthorityInfo]):
    def __init__(self, world: World, account_name: str, authority: AuthorityLevelRegular) -> None:
        self.world = world
        self.account_name = account_name
        self.authority = authority

    def validate(self):
        AccountNameValidator().validate(self.account_name)

    async def _run(self) -> AuthorityInfo:
        accounts = (await self.world.commands.find_accounts(accounts=[self.account_name])).result_or_raise
        account = accounts[0]

        authorities = []
        for auth, weight in [*account[self.authority].key_auths, *account[self.authority].account_auths]:
            authorities.append(Authority(account_or_public_key=auth, weight=weight))

        authority_info = AuthorityInfo(
            authority_owner_account_name=account.name,
            authority_type=self.authority,
            weight_threshold=account[self.authority].weight_threshold,
            authorities=authorities,
        )

        return authority_info
