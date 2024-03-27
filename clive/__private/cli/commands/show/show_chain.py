from dataclasses import dataclass
from datetime import timezone

from rich.console import Console
from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.core.formatters.humanize import (
    humanize_apr,
    humanize_asset,
    humanize_bytes,
    humanize_current_inflation_rate,
    humanize_hbd_interest_rate,
    humanize_hbd_print_rate,
    humanize_median_hive_price,
    humanize_natural_time,
    humanize_participation_count,
    humanize_string_to_format,
)


@dataclass(kw_only=True)
class ShowChain(WorldBasedCommand):
    async def _run(self) -> None:
        table = Table(title="Chain info", show_header=False)

        version = await self.world.node.api.database_api.get_version()
        witnesses_schedule = await self.world.node.api.database_api.get_witness_schedule()
        global_properties = await self.world.node.api.database_api.get_dynamic_global_properties()
        hardfork_properties = await self.world.node.api.database_api.get_hardfork_properties()
        current_price_feed = await self.world.node.api.database_api.get_current_price_feed()
        feed = await self.world.node.api.database_api.get_feed_history()

        account_creation_fee: str = ""
        if witnesses_schedule.median_props.account_creation_fee:
            account_creation_fee = witnesses_schedule.median_props.account_creation_fee.as_legacy()

        # Network properties
        table.add_row("Network properties:", f"{self.world.node.address}", end_section=True)
        table.add_row("chain type", f"{version.node_type}")
        table.add_row("chain id", f"{version.chain_id}")
        table.add_row(
            "head block time",
            (
                f"{global_properties.time.replace(tzinfo=timezone.utc)} ({humanize_natural_time(global_properties.time.astimezone().replace(tzinfo=None))})"
            ),
        )
        table.add_row("head block id", f"{global_properties.head_block_id}")
        table.add_row("head block produced by", f"{global_properties.current_witness}")
        table.add_row("head block number", f"{global_properties.head_block_number}")
        table.add_row("last irreversible block num", f"{global_properties.last_irreversible_block_num}")
        table.add_row("participation", f"{humanize_participation_count(global_properties.participation_count)}")
        table.add_row("hardfork version", f"{hardfork_properties.current_hardfork_version} ")
        table.add_row("witness majority version", f"{witnesses_schedule.majority_version}")
        table.add_row("maximum block size", f"{humanize_bytes(global_properties.maximum_block_size)}", end_section=True)

        # Financial
        table.add_row("Financial:", end_section=True)
        table.add_row("HBD savings APR", f"{humanize_hbd_interest_rate(global_properties.hbd_interest_rate)}")
        table.add_row("HBD print rate", f"{humanize_hbd_print_rate(global_properties.hbd_print_rate)}")
        table.add_row(
            "VESTS APR",
            (
                f"{humanize_apr(global_properties.head_block_number, global_properties.vesting_reward_percent, global_properties.virtual_supply, global_properties.total_vesting_fund_hive)}"
            ),
        )
        table.add_row(
            "current inflation rate", f"{humanize_current_inflation_rate(global_properties.head_block_number)}"
        )

        table.add_row(
            "median HIVE price",
            (
                f"{humanize_median_hive_price(current_price_feed, feed.current_median_history, feed.market_median_history)}"
            ),
        )
        table.add_row("account creation fee", f"{humanize_string_to_format(account_creation_fee)}")
        table.add_row(
            "VEST price",
            f"{humanize_string_to_format(humanize_asset(global_properties.total_vesting_shares/global_properties.total_vesting_fund_hive))}",
            end_section=True,
        )

        console = Console()
        console.print(table)
