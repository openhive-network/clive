from __future__ import annotations

from pathlib import Path
from typing import Final, Optional

import typer

from clive.__private.cli import common
from clive.__private.core.perform_actions_on_transaction import perform_actions_on_transaction
from clive.__private.storage.mock_database import PrivateKey
from clive.models.transfer_operation import TransferOperation

HELP: Final[str] = """
Transfer some funds to another account.
"""  # fmt: skip

transfer = typer.Typer(
    help=HELP,
    epilog='Example: [yellow]clive transfer --from clive --to clive --amount "1.000 HBD" --memo "For coffee!"[/]',
)


@transfer.callback(invoke_without_command=True)
def _main(
    from_: str = typer.Option(..., "--from", help="The account to transfer from."),
    to: str = typer.Option(..., help="The account to transfer to."),
    amount: str = typer.Option(..., help="The amount to transfer. (e.g. 2.500 HIVE)"),
    memo: Optional[str] = typer.Option(None, help="The memo to attach to the transfer."),
    broadcast: bool = common.Broadcast,
    sign: Optional[str] = common.Sign,
    profile: Optional[str] = common.Profile,
    password: Optional[str] = common.Password,
    save_file: Optional[str] = common.SaveFile,
) -> None:
    saved_args = locals()
    typer.echo(f"Transfer command invoked with params: {saved_args}")

    value, asset = amount.split(" ")

    perform_actions_on_transaction(
        TransferOperation(from_=from_, to=to, amount=value, asset=asset.upper(), memo=memo),
        sign_key=PrivateKey("temporary", sign) if sign else None,
        save_file_path=Path(save_file) if save_file else None,
        broadcast=broadcast,
    )
