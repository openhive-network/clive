from __future__ import annotations

from typing import TYPE_CHECKING, cast

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options
from clive.__private.cli.common.parsers import hive_asset

if TYPE_CHECKING:
    from clive.__private.models import Asset

claim = CliveTyper(name="claim", help="Manage the things you can collect.")


@claim.command(name="new-account-token")
async def process_claim_new_account_token(
    creator: str = options.account_name,
    fee: str | None = typer.Option(
        None,
        parser=hive_asset,
        help="Current account creation fee, if present must be exactly the value returned by clive show chain."
        " If not specified resource credits will be used to obtain token.",
        show_default=False,
    ),
    sign: str | None = options.sign,
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Obtain account creation token, pay either with HIVE or RC."""
    from clive.__private.cli.commands.process.process_claim_new_account_token import (  # noqa: PLC0415
        ProcessClaimNewAccountToken,
    )

    fee_ = cast("Asset.Hive", fee) if fee else None
    await ProcessClaimNewAccountToken(
        creator=creator,
        fee=fee_,
        sign=sign,
        broadcast=broadcast,
        save_file=save_file,
    ).run()
