from __future__ import annotations

from typing import TYPE_CHECKING, cast

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options

if TYPE_CHECKING:
    from clive.__private.models.asset import Asset

convert = CliveTyper(
    name="convert",
    help="""\
Convert assets between HBD and HIVE.

The --amount specifies what will be TAKEN from your balance, not what you will receive.
The received amount is determined after 3.5 days based on the market price.

Conversion types (determined by asset type in --amount):

- HBD → HIVE: Standard conversion. HBD is taken immediately; HIVE is received
  after 3.5 days based on median feed price at that time.

- HIVE → HBD: Collateralized conversion. HIVE is taken immediately; you receive
  HBD instantly (approx. half the HIVE value, using minimum feed price minus 5% fee).
  The other half is held as collateral and returned after 3.5 days. The returned
  amount may vary based on price changes during this period.
""",
)


@convert.callback(invoke_without_command=True)
async def process_convert(  # noqa: PLR0913
    amount: str = options.liquid_amount,
    from_account: str = options.from_account_name,
    request_id: int | None = typer.Option(
        None,
        "--request-id",
        help="Unique ID for the conversion request (if not given, will be automatically calculated).",
    ),
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    # Help text is defined in the CliveTyper help parameter above
    from clive.__private.cli.commands.process.process_convert import (  # noqa: PLC0415
        ProcessCollateralizedConvert,
        ProcessConvert,
    )
    from clive.__private.models.asset import Asset  # noqa: PLC0415

    amount_ = cast("Asset.LiquidT", amount)

    if isinstance(amount_, Asset.Hbd):
        # HBD → HIVE (standard convert)
        await ProcessConvert(
            owner=from_account,
            amount=amount_,
            request_id=request_id,
            sign_with=sign_with,
            broadcast=broadcast,
            save_file=save_file,
            autosign=autosign,
        ).run()
    else:
        # HIVE → HBD (collateralized convert)
        await ProcessCollateralizedConvert(
            owner=from_account,
            amount=amount_,
            request_id=request_id,
            sign_with=sign_with,
            broadcast=broadcast,
            save_file=save_file,
            autosign=autosign,
        ).run()
