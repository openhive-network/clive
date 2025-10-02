from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from beekeepy.exceptions import UnknownDecisionPathError

from clive.__private.cli.styling import colorize_error, colorize_ok, colorize_warning
from clive.__private.core.calculate_participation_count import calculate_participation_count_percent
from clive.__private.core.calculate_vests_to_hive_ratio import calculate_vests_to_hive_ratio
from clive.__private.core.commands.abc.command_data_retrieval import CommandDataRetrieval
from clive.__private.core.formatters.humanize import (
    align_to_dot,
    humanize_apr,
    humanize_bytes,
    humanize_current_inflation_rate,
    humanize_datetime,
    humanize_hbd_print_rate,
    humanize_hbd_savings_apr,
    humanize_median_hive_price,
    humanize_participation_count,
    humanize_vest_to_hive_ratio,
)
from clive.__private.core.iwax import (
    calculate_current_inflation_rate,
    calculate_hp_apr,
)
from clive.__private.core.percent_conversions import hive_percent_to_percent

if TYPE_CHECKING:
    from datetime import datetime
    from decimal import Decimal

    from clive.__private.core.node import Node
    from clive.__private.models.asset import Asset
    from clive.__private.models.schemas import (
        DynamicGlobalProperties,
        FeedHistory,
        HardforkProperties,
        PriceFeed,
        Version,
        WitnessSchedule,
    )


@dataclass
class HarvestedDataRaw:
    gdpo: DynamicGlobalProperties | None
    witness_schedule: WitnessSchedule | None
    version: Version | None
    hardfork_properties: HardforkProperties | None
    current_price_feed: PriceFeed | None
    feed: FeedHistory | None


@dataclass
class SanitizedData:
    gdpo: DynamicGlobalProperties
    witness_schedule: WitnessSchedule
    version: Version
    hardfork_properties: HardforkProperties
    current_price_feed: PriceFeed
    feed: FeedHistory
    account_creation_fee: Asset.Hive


@dataclass
class ChainData:
    account_creation_fee: Asset.Hive
    chain_id: str
    chain_type: str
    current_inflation_rate: Decimal
    hardfork_version: str
    hbd_print_rate: Decimal
    hbd_savings_apr: Decimal
    head_block_id: str
    head_block_number: int
    head_block_produced_by: str
    head_block_time: datetime
    last_irreversible_block_num: int
    maximum_block_size: int
    median_hive_price: PriceFeed
    participation: int
    vests_apr: Decimal
    vests_to_hive_ratio: Decimal
    witness_majority_version: str
    _current_median_history: PriceFeed
    _market_median_history: PriceFeed

    def __post_init__(self) -> None:
        self.__align_financial_data()

    @dataclass
    class AlignedFinancialData:
        pretty_account_creation_fee: str
        pretty_hbd_savings_apr: str
        pretty_hbd_print_rate: str
        pretty_vests_apr: str
        pretty_current_inflation_rate: str
        pretty_median_hive_price: str
        pretty_vests_to_hive_ratio: str
        hbd_savings_apr: str
        hbd_print_rate: str
        vests_apr: str
        current_inflation_rate: str
        vests_to_hive_ratio: str

    def __align_financial_data(self) -> None:
        to_align = [
            self.pretty_account_creation_fee,
            self.pretty_hbd_savings_apr,
            self.pretty_hbd_print_rate,
            self.pretty_vests_apr,
            self.pretty_current_inflation_rate,
            self.pretty_median_hive_price,
            self.pretty_vests_to_hive_ratio,
            str(self.hbd_savings_apr),
            str(self.hbd_print_rate),
            str(self.vests_apr),
            str(self.current_inflation_rate),
            str(self.vests_to_hive_ratio),
        ]
        self._aligned_financial_data = ChainData.AlignedFinancialData(*align_to_dot(*to_align))

    def get_aligned_financial_data(self) -> AlignedFinancialData:
        return self._aligned_financial_data

    @property
    def pretty_account_creation_fee(self) -> str:
        return self.account_creation_fee.as_legacy()

    @property
    def pretty_head_block_time(self) -> str:
        return humanize_datetime(self.head_block_time, with_relative_time=True)

    @property
    def pretty_vests_apr(self) -> str:
        return humanize_apr(self.vests_apr)

    @property
    def pretty_current_inflation_rate(self) -> str:
        return humanize_current_inflation_rate(self.head_block_number)

    @property
    def pretty_hbd_print_rate(self) -> str:
        return humanize_hbd_print_rate(self.hbd_print_rate)

    @property
    def pretty_hbd_savings_apr(self) -> str:
        return humanize_hbd_savings_apr(self.hbd_savings_apr)

    @property
    def pretty_participation(self) -> str:
        return humanize_participation_count(self.participation)

    @property
    def pretty_maximum_block_size(self) -> str:
        return humanize_bytes(self.maximum_block_size)

    @property
    def pretty_median_hive_price(self) -> str:
        return humanize_median_hive_price(self.median_hive_price)

    @property
    def pretty_vests_to_hive_ratio(self) -> str:
        return humanize_vest_to_hive_ratio(self.vests_to_hive_ratio)

    def get_hbd_print_rate(self, *, colorized: bool = True, aligned: bool = True, pretty: bool = True) -> str:
        if aligned:
            if pretty:
                hbd_print_rate = self._aligned_financial_data.pretty_hbd_print_rate
            else:
                hbd_print_rate = self._aligned_financial_data.hbd_print_rate
        elif pretty:
            hbd_print_rate = self.pretty_hbd_print_rate
        else:
            hbd_print_rate = str(self.hbd_print_rate)
        if colorized:
            return self.__colorize_hbd_print_rate(hbd_print_rate)
        return hbd_print_rate

    def get_median_hive_price(self, *, colorized: bool = True, aligned: bool = True, pretty: bool = True) -> str:
        if aligned:
            median_hive_price = self._aligned_financial_data.pretty_median_hive_price
        elif pretty:
            median_hive_price = self.pretty_median_hive_price
        else:
            median_hive_price = str(self.median_hive_price.base)
        if colorized:
            return self.__colorize_median_hive_price(median_hive_price)
        return median_hive_price

    def get_participation_count(self, *, colorized: bool = True, pretty: bool = True) -> str:
        participation = self.pretty_participation if pretty else str(self.participation)
        if colorized:
            return self.__colorize_participation_count(participation)
        return participation

    def __colorize_hbd_print_rate(self, hbd_print_rate: str) -> str:
        """Get status color for hbd print rate."""
        good_hbd_print_rate = 100
        if self.hbd_print_rate == good_hbd_print_rate:
            message = colorize_ok(hbd_print_rate)
        else:
            message = colorize_error(hbd_print_rate)
        return message

    def __colorize_median_hive_price(self, median_hive_price: str) -> str:
        """Get status color for median hive price."""
        same_current_and_market_median_history_base = (
            self._current_median_history.base == self._market_median_history.base
        )
        same_current_and_market_median_history_quote = (
            self._current_median_history.quote == self._market_median_history.quote
        )

        if same_current_and_market_median_history_base and same_current_and_market_median_history_quote:
            message = colorize_ok(median_hive_price)
        else:
            message = colorize_error(median_hive_price)
        return message

    def __colorize_participation_count(self, participation: str) -> str:
        """Get status color for participation count."""
        participation_count_percent = calculate_participation_count_percent(self.participation)
        critical_participation_count_percent = 33.0
        warning_participation_count_percent = 64.0
        if participation_count_percent <= critical_participation_count_percent:
            message = colorize_error(participation)
        elif participation_count_percent <= warning_participation_count_percent:
            message = colorize_warning(participation)
        else:
            message = colorize_ok(participation)
        return message


@dataclass(kw_only=True)
class ChainDataRetrieval(CommandDataRetrieval[HarvestedDataRaw, SanitizedData, ChainData]):
    node: Node

    async def _harvest_data_from_api(self) -> HarvestedDataRaw:
        async with await self.node.batch() as node:
            gdpo = await node.api.database_api.get_dynamic_global_properties()
            witness_schedule = await node.api.database_api.get_witness_schedule()
            version = await node.api.database_api.get_version()
            hardfork_properties = await node.api.database_api.get_hardfork_properties()
            current_price_feed = await node.api.database_api.get_current_price_feed()
            feed = await node.api.database_api.get_feed_history()
            return HarvestedDataRaw(gdpo, witness_schedule, version, hardfork_properties, current_price_feed, feed)
        raise UnknownDecisionPathError(f"{self.__class__.__name__}:_harvest_data_from_api")

    async def _sanitize_data(self, data: HarvestedDataRaw) -> SanitizedData:
        witness_schedule = self.__assert_witnesses_schedule(data.witness_schedule)
        return SanitizedData(
            gdpo=self.__assert_gdpo(data.gdpo),
            witness_schedule=witness_schedule,
            version=self.__assert_version(data.version),
            hardfork_properties=self.__assert_hardfork_properties(data.hardfork_properties),
            current_price_feed=self.__assert_current_price_feed(data.current_price_feed),
            feed=self.__assert_feed(data.feed),
            account_creation_fee=self.__assert_account_creation_fee(witness_schedule.median_props.account_creation_fee),
        )

    async def _process_data(self, data: SanitizedData) -> ChainData:
        return ChainData(
            account_creation_fee=data.account_creation_fee,
            chain_id=data.version.chain_id,
            chain_type=data.version.node_type,
            current_inflation_rate=calculate_current_inflation_rate(data.gdpo.head_block_number),
            hardfork_version=data.hardfork_properties.current_hardfork_version,
            hbd_print_rate=hive_percent_to_percent(data.gdpo.hbd_print_rate),
            hbd_savings_apr=hive_percent_to_percent(data.gdpo.hbd_interest_rate),
            head_block_id=data.gdpo.head_block_id,
            head_block_number=data.gdpo.head_block_number,
            head_block_produced_by=data.gdpo.current_witness,
            head_block_time=data.gdpo.time,
            last_irreversible_block_num=data.gdpo.last_irreversible_block_num,
            maximum_block_size=data.gdpo.maximum_block_size,
            median_hive_price=data.current_price_feed,
            participation=data.gdpo.participation_count,
            vests_apr=calculate_hp_apr(data.gdpo),
            vests_to_hive_ratio=calculate_vests_to_hive_ratio(data.gdpo),
            witness_majority_version=data.witness_schedule.majority_version,
            _current_median_history=data.feed.current_median_history,
            _market_median_history=data.feed.market_median_history,
        )

    def __assert_gdpo(self, gdpo: DynamicGlobalProperties | None) -> DynamicGlobalProperties:
        assert gdpo, "DynamicGlobalProperties are missing."
        return gdpo

    def __assert_witnesses_schedule(self, witnesses_schedule: WitnessSchedule | None) -> WitnessSchedule:
        assert witnesses_schedule, "WitnessSchedule are missing."
        return witnesses_schedule

    def __assert_account_creation_fee(self, account_creation_fee: Asset.Hive | None) -> Asset.Hive:
        assert account_creation_fee, "Account creation fee is None."
        return account_creation_fee

    def __assert_version(self, version: Version | None) -> Version:
        assert version, "Version is missing."
        return version

    def __assert_hardfork_properties(self, hardfork_properties: HardforkProperties | None) -> HardforkProperties:
        assert hardfork_properties, "HardforkProperties are missing."
        return hardfork_properties

    def __assert_current_price_feed(self, current_price_feed: PriceFeed | None) -> PriceFeed:
        assert current_price_feed, "CurrentPriceFeed is missing."
        return current_price_feed

    def __assert_feed(self, feed_history: FeedHistory | None) -> FeedHistory:
        assert feed_history, "FeedHistory is missing."
        return feed_history
