from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.print_cli import print_cli, print_content_not_available
from clive.__private.core.formatters.humanize import humanize_datetime
from clive.__private.models.asset import Asset

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.order_data import OrderData, OrderInfo


@dataclass(kw_only=True)
class ShowOrders(WorldBasedCommand):
    account_name: str

    async def _run(self) -> None:
        wrapper = await self.world.commands.retrieve_order_data(account_name=self.account_name)
        result: OrderData = wrapper.result_or_raise

        if not result.orders:
            print_content_not_available(f"Account `{self.account_name}` has no open orders")
            return

        table = Table(title=f"Open limit orders for account: {self.account_name}")

        table.add_column("Order ID", justify="right", style="cyan", no_wrap=True)
        table.add_column("Type", justify="center", style="yellow", no_wrap=True)
        table.add_column("Selling", justify="right", style="green", no_wrap=True)
        table.add_column("For (min)", justify="right", style="green", no_wrap=True)
        table.add_column("Price", justify="right", style="magenta", no_wrap=True)
        table.add_column("Created (UTC)", justify="right", style="green", no_wrap=True)
        table.add_column("Expires (UTC)", justify="right", style="green", no_wrap=True)

        order_info: OrderInfo
        for order_info in result.orders:
            # Determine order type based on what's being sold
            order_type = "SELL HIVE" if isinstance(order_info.sell_asset, Asset.Hive) else "SELL HBD"

            # Calculate price
            price_str = f"{order_info.price:.6f}"

            table.add_row(
                f"{order_info.orderid}",
                order_type,
                f"{Asset.to_legacy(order_info.sell_asset)}",
                f"{Asset.to_legacy(order_info.receive_asset)}",
                price_str,
                f"{humanize_datetime(order_info.created)}",
                f"{humanize_datetime(order_info.expiration)}",
            )
        print_cli(table)
