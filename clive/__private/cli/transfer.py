from pathlib import Path
from typing import Final

import typer

from clive.__private.cli.common import Common, common_options
from clive.__private.core.perform_actions_on_transaction import perform_actions_on_transaction
from clive.__private.storage.mock_database import PrivateKeyAlias
from clive.models import Asset
from schemas.operations import TransferOperation

HELP: Final[str] = """
Transfer some funds to another account.
"""  # fmt: skip

transfer = typer.Typer(
    help=HELP,
    epilog='Example: [yellow]clive transfer --from clive --to clive --amount "1.000 HBD" --memo "For coffee!"[/]',
)


@transfer.callback(invoke_without_command=True)
@common_options
def _main(
    ctx: typer.Context,
    from_: str = typer.Option(..., "--from", help="The account to transfer from."),
    to: str = typer.Option(..., help="The account to transfer to."),
    amount: str = typer.Option(..., help="The amount to transfer. (e.g. 2.500 HIVE)"),
    memo: str = typer.Option("", help="The memo to attach to the transfer."),
) -> None:
    common = Common(**ctx.params)
    if common.world is None:
        typer.echo("world is none")
        return
    typer.echo(f"{common.world.profile_data.name=}")

    perform_actions_on_transaction(
        TransferOperation(from_=from_, to=to, amount=Asset.from_legacy(amount.upper()), memo=memo),
        beekeeper=common.world.beekeeper,
        node=common.world.node,
        sign_key=PrivateKeyAlias(common.sign) if common.sign else None,
        save_file_path=Path(common.save_file) if common.save_file else None,
        broadcast=common.broadcast,
        chain_id=common.world.node.chain_id,
    )
