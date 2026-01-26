from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import TYPE_CHECKING, cast

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options
from clive.__private.cli.common.parsers import hive_datetime, liquid_asset

if TYPE_CHECKING:
    from clive.__private.models.asset import Asset

order = CliveTyper(name="order", help="Manage limit orders on the internal market.")

# Default expiration is 28 days from now
DEFAULT_EXPIRATION_DAYS = 28


def _get_default_expiration() -> str:
    """Get default expiration datetime as string (28 days from now)."""
    from datetime import UTC  # noqa: PLC0415

    from clive.__private.core.constants.date import TIME_FORMAT_WITH_SECONDS  # noqa: PLC0415

    future_time = datetime.now(UTC) + timedelta(days=DEFAULT_EXPIRATION_DAYS)
    return future_time.strftime(TIME_FORMAT_WITH_SECONDS)


def _parse_price(raw: str) -> Decimal:
    """Parse a price value (positive decimal number)."""
    try:
        value = Decimal(raw)
    except InvalidOperation:
        raise typer.BadParameter(f"Invalid price format: '{raw}'. Expected a decimal number.") from None

    if value <= 0:
        raise typer.BadParameter("Price must be a positive number.")
    return value


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
    price: str | None = typer.Option(
        None,
        "--price",
        parser=_parse_price,
        help=(
            "Price per unit of sold asset. min_to_receive = amount_to_sell * price."
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
        help="When the order expires (format: YYYY-MM-DDTHH:MM:SS). Default: 28 days from now.",
    ),
    fill_or_kill: bool = typer.Option(  # noqa: FBT001
        False,  # noqa: FBT003
        "--fill-or-kill/--no-fill-or-kill",
        help="If set, the order must be filled completely or not at all.",
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
        price=cast("Decimal | None", price),
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
