from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
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
        table.add_column("For sale", justify="right", style="green", no_wrap=True)
        table.add_column("To receive", justify="right", style="green", no_wrap=True)
        table.add_column("Price HBD/HIVE", justify="right", style="magenta", no_wrap=True)
        table.add_column("Created (UTC)", justify="right", style="green", no_wrap=True)
        table.add_column("Expires (UTC)", justify="right", style="green", no_wrap=True)

        def get_normalized_price(order: OrderInfo) -> Decimal:
            """Get price normalized to HBD/HIVE (invert for SELL HBD orders)."""
            if isinstance(order.remaining_sell_asset, Asset.Hbd):
                return Decimal(1) / order.price if order.price != 0 else Decimal(0)
            return order.price

        # Sort orders by normalized price (HBD/HIVE)
        sorted_orders = sorted(result.orders, key=get_normalized_price)

        order_info: OrderInfo
        for order_info in sorted_orders:
            # Determine order type based on what's being sold
            order_type = "SELL HIVE" if isinstance(order_info.remaining_sell_asset, Asset.Hive) else "SELL HBD"

            # Calculate price normalized to HBD/HIVE
            normalized_price = get_normalized_price(order_info)
            price_str = f"{normalized_price:.10f}".rstrip("0").rstrip(".")

            table.add_row(
                f"{order_info.orderid}",
                order_type,
                Asset.pretty_amount(order_info.remaining_sell_asset),
                Asset.pretty_amount(order_info.remaining_receive_asset),
                price_str,
                humanize_datetime(order_info.created),
                humanize_datetime(order_info.expiration),
            )
        print_cli(table)
