from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime

from clive.__private.core.commands.abc.command_data_retrieval import (
    CommandDataRetrieval,
)
from clive.models.aliased import DynamicGlobalProperties, ListWitnessVotes, ListWitnesses, WitnessesFundament, ListWitnessVotesFundament

if TYPE_CHECKING:
    from clive.__private.core.node import Node


@dataclass
class Witness:
    name: str
    created: datetime = field(default_factory=lambda: datetime.fromtimestamp(0))
    voted: bool = False
    votes: str = "?"
    rank: int | None = None
    missed_blocks: int = 0
    last_block: int = 0
    price_feed: str = "?"
    version: str = ""
    url: str = ""


@dataclass
class HarvestedDataRaw:
    gdpo: DynamicGlobalProperties | None = None
    list_witnesses_votes: ListWitnessVotes | None = None
    first_150_witnesses: ListWitnesses | None = None


@dataclass
class SanitizedData:
    gdpo: DynamicGlobalProperties
    list_witnesses_votes: list[WitnessesFundament]
    first_150_witnesses: list[WitnessesFundament]


@dataclass
class GovernanceData:
    witnesses: dict[str, Witness] | None = None
    witnesses_names: list[str] | None = None
    number_of_votes: int = 0


@dataclass(kw_only=True)
class GovernanceDataRetrieval(CommandDataRetrieval[HarvestedDataRaw, SanitizedData, GovernanceData]):
    node: Node
    account_name: str

    async def _harvest_data_from_api(self) -> HarvestedDataRaw:
        async with self.node.batch() as node:
            return HarvestedDataRaw(
                await node.api.database_api.get_dynamic_global_properties(),
                await node.api.database_api.list_witness_votes(start=(self.account_name, ""), limit=30, order="by_account_witness"),
                await node.api.database_api.list_witnesses(start=(1000000000000000000, ""), limit=150, order="by_vote_name")
            )

    async def _sanitize_data(self, data: HarvestedDataRaw) -> SanitizedData:
        return SanitizedData(
            gdpo=self.__assert_gdpo(data.gdpo),
            core_account=self.__assert_core_account(data.core_account),
            pending_transfers=self.__assert_pending_transfers(data.savings_withdrawals),
            )

    async def _process_data(self, data: SanitizedData) -> GovernanceData:
        return GovernanceData(
            hbd_interest_rate=data.dgpo.hbd_interest_rate,
            last_interest_payment=data.core_account.savings_hbd_last_interest_payment,
            pending_transfers=data.pending_transfers,
        )
    def __assert_gdpo(self, data: DynamicGlobalProperties | None) -> DynamicGlobalProperties:
        assert data is not None, "DynamicGlobalProperties data is missing"
        return data

    def __assert_witnesses_votes(self, data: ListWitnessVotes | None) -> list[ListWitnessVotesFundament]:
        assert data is not None, "ListWitnessVotes data is missing"

        account = data.accounts[0]
        witnesses_votes = []
        assert account.name == self.account_name, "Invalid account name"
        return account

        def __assert_pending_transfers(self, data: FindSavingsWithdrawals | None) -> list[SavingsWithdrawals]:
            assert data is not None, "FindSavingsWithdrawals data is missing"
            return data.withdrawals





