from __future__ import annotations

from typing import TYPE_CHECKING, Final

from clive.__private.core.accounts.accounts import TrackedAccount
from clive.__private.core.commands.data_retrieval.witnesses_data import (
    WitnessData,
    WitnessesData,
    WitnessesDataRetrieval,
)
from clive.__private.core.commands.find_accounts import AccountNotFoundError as CoreAccountNotFoundError
from clive.__private.core.profile import Profile
from clive.__private.py.data_classes import Accounts, Authority, AuthorityInfo, Balances, Witness, WitnessesResult
from clive.__private.py.exceptions import AccountNotFoundError, InvalidAuthorityTypeError
from clive.__private.py.foundation.base import CommandBase
from clive.__private.py.validators import AccountNameValidator, PageNumberValidator, PageSizeValidator

if TYPE_CHECKING:
    from clive.__private.core.types import AuthorityLevelRegular
    from clive.__private.core.world import World


class ShowProfiles(CommandBase[list[str]]):
    async def _run(self) -> list[str]:
        return Profile.list_profiles()


class ShowBalances(CommandBase[Balances]):
    def __init__(self, world: World, account_name: str) -> None:
        self.world = world
        self.account_name = account_name

    async def validate(self) -> None:
        AccountNameValidator().validate(self.account_name)

    async def _run(self) -> Balances:
        await self._ensure_account_exists()
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

    async def _ensure_account_exists(self) -> None:
        """Check if the account exists on the blockchain."""
        try:
            await self.world.commands.find_accounts(accounts=[self.account_name])
        except CoreAccountNotFoundError as err:
            raise AccountNotFoundError(self.account_name) from err


class ShowAccounts(CommandBase[Accounts]):
    def __init__(self, world: World) -> None:
        self.world = world

    async def _run(self) -> Accounts:
        profile = self.world.profile
        return Accounts(
            working_account=profile.accounts.working.name if profile.accounts.has_working_account else None,
            tracked_accounts=tuple(account.name for account in profile.accounts.tracked),
            known_accounts=tuple(account.name for account in profile.accounts.known),
        )


class ShowWitnesses(CommandBase[WitnessesResult]):
    """
    Command to retrieve witnesses with pagination support.

    Note:
        If page_no exceeds available pages, returns empty witnesses list
        without raising an error. The total_count field in the result
        can be used to calculate the maximum valid page number.
    """

    def __init__(self, world: World, account_name: str, page_size: int, page_no: int) -> None:
        self.world = world
        self.account_name = account_name
        self.page_size = page_size
        self.page_no = page_no

    async def validate(self) -> None:
        AccountNameValidator().validate(self.account_name)
        PageSizeValidator().validate(self.page_size)
        PageNumberValidator().validate(self.page_no)

    async def _run(self) -> WitnessesResult:
        wrapper = await self.world.commands.find_accounts(accounts=[self.account_name])
        try:
            accounts = wrapper.result_or_raise
        except CoreAccountNotFoundError as err:
            raise AccountNotFoundError(self.account_name) from err
        if not accounts:
            raise AccountNotFoundError(self.account_name)
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

        witnesses = tuple(
            Witness(
                voted=witness.voted,
                rank=witness.rank,
                witness_name=witness.name,
                votes=witness.votes_raw,
                votes_display=witness.votes,
                created=witness.created,
                missed_blocks=witness.missed_blocks,
                last_block=witness.last_block,
                price_feed=witness.price_feed,
                version=witness.version,
            )
            for witness in witnesses_chunk
        )

        return WitnessesResult(
            witnesses=witnesses,
            total_count=len(witnesses_list),
            proxy=proxy,
        )


class ShowAuthority(CommandBase[AuthorityInfo]):
    VALID_AUTHORITIES: Final[frozenset[str]] = frozenset({"owner", "active", "posting"})

    def __init__(self, world: World, account_name: str, authority: AuthorityLevelRegular) -> None:
        self.world = world
        self.account_name = account_name
        self.authority = authority

    async def validate(self) -> None:
        AccountNameValidator().validate(self.account_name)
        if self.authority not in self.VALID_AUTHORITIES:
            raise InvalidAuthorityTypeError(self.authority, self.VALID_AUTHORITIES)

    async def _run(self) -> AuthorityInfo:
        accounts = (await self.world.commands.find_accounts(accounts=[self.account_name])).result_or_raise
        account = accounts[0]

        authorities = tuple(
            Authority(account_or_public_key=auth, weight=weight)
            for auth, weight in [*account[self.authority].key_auths, *account[self.authority].account_auths]
        )

        return AuthorityInfo(
            authority_owner_account_name=account.name,
            authority_type=self.authority,
            weight_threshold=account[self.authority].weight_threshold,
            authorities=authorities,
        )
