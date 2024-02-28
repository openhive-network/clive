from dataclasses import dataclass
from datetime import datetime

from rich.console import Console
from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.core.formatters.humanize import humanize_asset
from schemas.fields.hive_datetime import HiveDateTime


def get_approximate_relative_time_string(  # noqa: PLR0911
    event_time: datetime, relative_to_time: datetime, default_ago: str = " ago"
) -> str:
    """Function based on 'fc::get_approximate_relative_time_string' from hived."""
    ago = default_ago
    time_difference = relative_to_time - event_time

    if time_difference.total_seconds() < 0:
        ago = " in the future"
        time_difference = -time_difference

    seconds_ago = int(time_difference.total_seconds())

    if seconds_ago < 90:  # noqa: PLR2004
        return f"{seconds_ago} second{'s' if seconds_ago > 1 else ''}{ago}"

    minutes_ago = (seconds_ago + 30) // 60
    if minutes_ago < 90:  # noqa: PLR2004
        return f"{minutes_ago} minute{'s' if minutes_ago > 1 else ''}{ago}"

    hours_ago = (minutes_ago + 30) // 60
    if hours_ago < 90:  # noqa: PLR2004
        return f"{hours_ago} hour{'s' if hours_ago > 1 else ''}{ago}"

    days_ago = (hours_ago + 12) // 24
    if days_ago < 90:  # noqa: PLR2004
        return f"{days_ago} day{'s' if days_ago > 1 else ''}{ago}"

    weeks_ago = (days_ago + 3) // 7
    if weeks_ago < 70:  # noqa: PLR2004
        return f"{weeks_ago} week{'s' if weeks_ago > 1 else ''}{ago}"

    months_ago = (days_ago + 15) // 30
    if months_ago < 12:  # noqa: PLR2004
        return f"{months_ago} month{'s' if months_ago > 1 else ''}{ago}"

    years_ago = days_ago // 365
    result = f"{years_ago} year{'s' if years_ago > 1 else ''}"
    if months_ago < 12 * 5:
        leftover_days = days_ago - (years_ago * 365)
        leftover_months = (leftover_days + 15) // 30
        if leftover_months:
            result += f" {leftover_months} month{'s' if leftover_months > 1 else ''}"
    result += ago
    return result


@dataclass(kw_only=True)
class ShowChain(WorldBasedCommand):
    async def _run(self) -> None:
        table = Table(title="Chain info", show_header=False)

        witnesses_schedule = await self.world.node.api.database_api.get_witness_schedule()
        global_properties = await self.world.node.api.database_api.get_dynamic_global_properties()
        hardfork_properties = await self.world.node.api.database_api.get_hardfork_properties()
        current_price_feed = await self.world.node.api.database_api.get_current_price_feed()
        chain_id = await self.world.node.chain_id

        account_creation_fee: str | None = None
        if witnesses_schedule.median_props.account_creation_fee:
            account_creation_fee = witnesses_schedule.median_props.account_creation_fee.as_legacy()

        table.add_row(f"head_block_number: {global_properties.head_block_number}")
        table.add_row(f"head_block_id: {global_properties.head_block_id}")
        table.add_row(f"time: {global_properties.time}")
        table.add_row(f"current_witness: {global_properties.current_witness}")
        table.add_row(f"hbd_interest_rate: {global_properties.hbd_interest_rate}")
        table.add_row(f"hbd_print_rate: {global_properties.hbd_print_rate}")
        table.add_row(f"maximum_block_size: {global_properties.maximum_block_size}")
        table.add_row(f"last_irreversible_block_num: {global_properties.last_irreversible_block_num}")
        table.add_row(f"witness_majority_version: {witnesses_schedule.majority_version}")
        table.add_row(f"hardfork_version: {hardfork_properties.current_hardfork_version} ")
        table.add_row(f"head_block_num: {global_properties.head_block_number}")
        table.add_row(
            "head_block_age:"
            f" {get_approximate_relative_time_string(global_properties.time.replace(tzinfo=None), HiveDateTime.now().replace(tzinfo=None))}"
        )
        table.add_row(f"participation: {100*global_properties.participation_count/128}")
        table.add_row(
            f"median_hbd_price: base={current_price_feed.base.as_legacy()},"
            f" quote={current_price_feed.quote.as_legacy()}"
        )
        table.add_row(f"account_creation_fee: {account_creation_fee}")
        table.add_row(f"chain_id: {chain_id}")
        table.add_row(
            "vest_price:"
            f" {humanize_asset(global_properties.total_vesting_shares/global_properties.total_vesting_fund_hive)}"
        )

        console = Console()
        console.print(table)
