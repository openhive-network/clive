from __future__ import annotations

from datetime import datetime  # noqa: TC003 - Required at runtime for Typer type annotations
from typing import TYPE_CHECKING, cast

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options
from clive.__private.cli.common.parameters.styling import stylized_help
from clive.__private.cli.common.parsers import hbd_asset, hive_datetime, liquid_asset

if TYPE_CHECKING:
    from clive.__private.models.asset import Asset

ORDER_HELP = """\
Manage limit orders on the internal HIVE/HBD market.

The internal market allows direct trading between HIVE and HBD without external exchanges.
Limit orders specify a price at which you're willing to trade and remain open until
filled, cancelled, or expired (default: 28 days).

To view your open orders: clive show orders
To view all market orders: clive show orders --account-name <any_account>

Examples:
  # Sell 100 HIVE for at least 25 HBD
  clive process order create --amount-to-sell "100.000 HIVE" --min-to-receive "25.000 HBD"

  # Sell 100 HIVE at 0.250 HBD per HIVE (equivalent to above)
  clive process order create --amount-to-sell "100.000 HIVE" --price "0.250 HBD"

  # Sell HBD for HIVE
  clive process order create --amount-to-sell "25.000 HBD" --min-to-receive "100.000 HIVE"
"""

order = CliveTyper(name="order", help=ORDER_HELP)


@order.command(name="create")
async def process_order_create(  # noqa: PLR0913
    from_account: str = options.from_account_name,
    amount_to_sell: str = typer.Option(
        ...,
        "--amount-to-sell",
        parser=liquid_asset,
        help="Amount to sell (HIVE or HBD, e.g., 100.000 HIVE).",
    ),
    min_to_receive: str | None = typer.Option(
        None,
        "--min-to-receive",
        parser=liquid_asset,
        help="Minimum amount to receive (opposite asset, e.g., 25.000 HBD). Mutually exclusive with --price.",
    ),
    price_value: str | None = typer.Option(
        None,
        "--price",
        parser=hbd_asset,
        help=(
            "Price of 1 HIVE in HBD (e.g., 0.25hbd). "
            "When selling HIVE, you receive HBD; when selling HBD, you receive HIVE. "
            "Mutually exclusive with --min-to-receive."
        ),
    ),
    order_id: int | None = typer.Option(
        None,
        "--order-id",
        help="Unique identifier for this order. If not given, will be automatically calculated.",
    ),
    expiration: datetime | None = typer.Option(
        None,
        "--expiration",
        parser=hive_datetime,
        help=stylized_help(
            "When the order expires (max 28 days)."
            " Formats: absolute (2024-12-31, 2024-12-31T14:30:00) or relative (+14d, +2w).",
            default="28 days from now",
        ),
    ),
    fill_or_kill: bool = typer.Option(  # noqa: FBT001
        False,  # noqa: FBT003
        "--fill-or-kill/--no-fill-or-kill",
        help=(
            "If set, the order must be filled completely and immediately, or it will be cancelled. "
            "Use this when you want to trade only if a matching order already exists on the market. "
            "Without this flag, unfilled orders remain open until expiration."
        ),
    ),
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Create a new limit order on the internal market."""
    from clive.__private.cli.commands.process.process_order import ProcessOrderCreate  # noqa: PLC0415

    await ProcessOrderCreate(
        from_account=from_account,
        amount_to_sell=cast("Asset.LiquidT", amount_to_sell),
        min_to_receive=cast("Asset.LiquidT | None", min_to_receive),
        price=cast("Asset.Hbd | None", price_value),
        order_id=order_id,
        expiration=expiration,
        fill_or_kill=fill_or_kill,
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    ).run()


@order.command(name="cancel")
async def process_order_cancel(  # noqa: PLR0913
    from_account: str = options.from_account_name,
    order_id: int = typer.Option(..., "--order-id", help="ID of the order to cancel."),
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Cancel an existing limit order."""
    from clive.__private.cli.commands.process.process_order import ProcessOrderCancel  # noqa: PLC0415

    await ProcessOrderCancel(
        from_account=from_account,
        order_id=order_id,
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    ).run()
