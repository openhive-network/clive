from pathlib import Path
from typing import Final

import typer

from clive.__private.cli.common.operation_common import OperationCommon
from clive.__private.core.keys import PublicKey
from clive.__private.core.perform_actions_on_transaction import perform_actions_on_transaction
from clive.models import Asset
from schemas.operations import TransferOperation

HELP: Final[str] = """
Transfer some funds to another account.
"""  # fmt: skip

transfer = typer.Typer(
    help=HELP,
    epilog='Example: [yellow]clive transfer --sign mykeyalias --to clive --amount "1.000 HBD" --memo "For coffee!"[/]',
)


@transfer.callback(invoke_without_command=True)
@OperationCommon.decorator
def _main(
    ctx: typer.Context,
    from_: str = typer.Option(..., "--from", help="The account to transfer from.", show_default=False),
    to: str = typer.Option(..., help="The account to transfer to.", show_default=False),
    amount: str = typer.Option(..., help="The amount to transfer. (e.g. 2.500 HIVE)", show_default=False),
    memo: str = typer.Option("", help="The memo to attach to the transfer."),
) -> None:
    common = OperationCommon(**ctx.params)

    perform_actions_on_transaction(
        TransferOperation(from_=from_, to=to, amount=Asset.from_legacy(amount.upper()), memo=memo),
        beekeeper=common.world.beekeeper,
        node=common.world.node,
        sign_key=PublicKey(value=common.sign) if common.sign else None,
        save_file_path=Path(common.save_file) if common.save_file else None,
        broadcast=common.broadcast,
        chain_id=common.world.node.chain_id,
    )
