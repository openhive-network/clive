from dataclasses import dataclass

from rich.console import Console
from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.core.formatters.humanize import humanize_asset, humanize_natural_time
from clive.__private.core.iwax import calculate_hp_apr


@dataclass(kw_only=True)
class ShowChain(WorldBasedCommand):
    async def _run(self) -> None:
        table = Table(title="Chain info", show_header=False)

        node_type = (await self.world.node.api.database_api.get_version()).node_type
        witnesses_schedule = await self.world.node.api.database_api.get_witness_schedule()
        global_properties = await self.world.node.api.database_api.get_dynamic_global_properties()
        hardfork_properties = await self.world.node.api.database_api.get_hardfork_properties()
        current_price_feed = await self.world.node.api.database_api.get_current_price_feed()
        chain_id = await self.world.node.chain_id

        account_creation_fee: str | None = None
        if witnesses_schedule.median_props.account_creation_fee:
            account_creation_fee = witnesses_schedule.median_props.account_creation_fee.as_legacy()

        apr = calculate_hp_apr(
            global_properties.head_block_number,
            global_properties.vesting_reward_percent,
            global_properties.virtual_supply,
            global_properties.total_vesting_fund_hive,
        )

        table.add_row("chain", f"name={node_type} id={chain_id} ")
        table.add_row("head_block_number", f"{global_properties.head_block_number}")
        table.add_row("head_block_id", f"{global_properties.head_block_id}")
        table.add_row("time", f"{global_properties.time.astimezone()}")
        table.add_row("current_witness", f"{global_properties.current_witness}")
        table.add_row("hbd_interest_rate", f"{global_properties.hbd_interest_rate}")
        table.add_row("apr", f"{apr}")
        table.add_row("hbd_print_rate", f"{global_properties.hbd_print_rate}")
        table.add_row("maximum_block_size", f"{global_properties.maximum_block_size}")
        table.add_row("last_irreversible_block_num", f"{global_properties.last_irreversible_block_num}")
        table.add_row("witness_majority_version", f"{witnesses_schedule.majority_version}")
        table.add_row("hardfork_version", f"{hardfork_properties.current_hardfork_version} ")
        table.add_row("head_block_num", f"{global_properties.head_block_number}")
        table.add_row(
            "head_block_age", f"{humanize_natural_time(global_properties.time.astimezone().replace(tzinfo=None))}"
        )
        table.add_row("participation", f"{100*global_properties.participation_count/128}")
        table.add_row(
            "median_hbd_price",
            f"base={current_price_feed.base.as_legacy()} quote={current_price_feed.quote.as_legacy()}",
        )
        table.add_row("account_creation_fee", f"{account_creation_fee}")
        table.add_row(
            "vest_price",
            f"{humanize_asset(global_properties.total_vesting_shares/global_properties.total_vesting_fund_hive)}",
        )

        console = Console()
        console.print(table)
