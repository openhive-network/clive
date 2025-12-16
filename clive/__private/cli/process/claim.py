from __future__ import annotations

from typing import TYPE_CHECKING, cast

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options
from clive.__private.cli.common.parsers import hive_asset

if TYPE_CHECKING:
    from clive.__private.models.asset import Asset

claim = CliveTyper(name="claim", help="Manage the things you can collect.")


@claim.command(name="new-account-token")
async def process_claim_new_account_token(  # noqa: PLR0913
    creator: str = options.account_name,
    fee: str | None = typer.Option(
        None,
        parser=hive_asset,
        help="Current account creation fee, if present must be exactly the value returned by clive show chain."
        " If not specified resource credits will be used to obtain token.",
    ),
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast,  # noqa: FBT001
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
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    ).run()


@claim.command(name="rewards")
async def process_claim_rewards(
    account_name: str = options.account_name,
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Claim all pending blockchain rewards in HBD, HP (VESTS), and HIVE. Requires posting authority."""
    from clive.__private.cli.commands.process.process_claim_rewards import ProcessClaimRewards  # noqa: PLC0415

    await ProcessClaimRewards(
        account_name=account_name,
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    ).run()
