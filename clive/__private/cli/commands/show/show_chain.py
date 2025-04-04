from __future__ import annotations

from dataclasses import dataclass

from rich.console import Console
from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.core.formatters.data_labels import (
    CURRENT_INFLATION_RATE_LABEL,
    HBD_PRINT_RATE_LABEL,
    HBD_SAVINGS_APR_LABEL,
    MEDIAN_HIVE_PRICE_LABEL,
    PARTICIPATION_COUNT_LABEL,
    VEST_HIVE_RATIO_LABEL,
)


@dataclass(kw_only=True)
class ShowChain(WorldBasedCommand):
    async def _run(self) -> None:
        wrapper = await self.world.commands.retrieve_chain_data()
        data = wrapper.result_or_raise
        table = Table(title="Chain info", show_header=False)

        table.add_row("Network properties:", f"{self.world.node.http_endpoint}", end_section=True)
        table.add_row("chain type", data.chain_type)
        table.add_row("chain id", data.chain_id)
        table.add_row("head block time", data.pretty_head_block_time)
        table.add_row("head block id", data.head_block_id)
        table.add_row("head block produced by", data.head_block_produced_by)
        table.add_row("head block number", f"{data.head_block_number}")
        table.add_row("last irreversible block num", f"{data.last_irreversible_block_num}")
        table.add_row(PARTICIPATION_COUNT_LABEL, data.get_participation_count())
        table.add_row("hardfork version", data.hardfork_version)
        table.add_row("witness majority version", data.witness_majority_version)
        table.add_row("maximum block size", data.pretty_maximum_block_size, end_section=True)
        table.add_row("Financial:", end_section=True)

        financial_data = data.get_aligned_financial_data()
        table.add_row(HBD_SAVINGS_APR_LABEL, financial_data.pretty_hbd_savings_apr)
        table.add_row("VESTS APR", financial_data.pretty_vests_apr)
        table.add_row(HBD_PRINT_RATE_LABEL, data.get_hbd_print_rate())
        table.add_row(CURRENT_INFLATION_RATE_LABEL, financial_data.pretty_current_inflation_rate)
        table.add_row(MEDIAN_HIVE_PRICE_LABEL, data.get_median_hive_price())
        table.add_row("account creation fee", financial_data.pretty_account_creation_fee)
        table.add_row(VEST_HIVE_RATIO_LABEL, financial_data.vests_to_hive_ratio, end_section=True)

        console = Console()
        console.print(table)
