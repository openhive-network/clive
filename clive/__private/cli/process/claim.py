from typing import TYPE_CHECKING, Optional, cast

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import OperationOptionsGroup, options
from clive.__private.cli.common.parsers import hive_asset

if TYPE_CHECKING:
    from clive.__private.models import Asset

claim = CliveTyper(name="claim", help="Manage the things you can collect.")


@claim.command(name="new-account-token", param_groups=[OperationOptionsGroup])
async def process_claim_new_account_token(
    ctx: typer.Context,  # noqa: ARG001
    creator: str = options.account_name,
    fee: Optional[str] = typer.Option(
        None,
        parser=hive_asset,
        help="Current account creation fee, if present must be exactly the value returned by clive show chain."
        " If not specified resource credits will be used to obtain token.",
        show_default=False,
    ),
) -> None:
    """Obtain account creation token, pay either with HIVE or RC."""
    from clive.__private.cli.commands.process.process_claim_new_account_token import ProcessClaimNewAccountToken

    common = OperationOptionsGroup.get_instance()
    fee_ = cast("Asset.Hive", fee) if fee else None
    await ProcessClaimNewAccountToken(**common.as_dict(), creator=creator, fee=fee_).run()
